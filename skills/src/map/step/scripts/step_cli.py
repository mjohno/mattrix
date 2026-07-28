#!/usr/bin/env python3
"""Lightweight helper for STEP-<slug>.yaml files.

Primary protocol commands:
  start    create a STEP file
  context  show resumable state
  approve  merge lessons and record the exactly-approved chat proposal before execution
  record   record current-step evidence, goal-progress retro, and next choices
  gate     lint, then run built-in context for the next approval gate
  lint     validate state shape


Exit codes:
  0 success
  1 usage/argument error
  2 lint failure
  3 file/env error
  4 YAML parse or schema-shape error during an operation

Self-test:
  step_cli.py --test

Dependency:
  PyYAML is required.

Preview:
  step_cli.py --dry-run <mutating operation>
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only when dependency is absent.
    yaml = None  # type: ignore[assignment]

log = logging.getLogger(__name__)

EXIT_OK = 0
EXIT_USAGE = 1
EXIT_LINT = 2
EXIT_FILE = 3
EXIT_SCHEMA = 4

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STEP_FIELD_ORDER = ["slug", "intent", "criteria", "do", "validate", "retro", "next_steps", "recommendation"]
PROTOCOL_HELP = """step protocol workflow:
  1. start --goal ...                  create STEP-<slug>.yaml with no approved steps
  2. context                           inspect resumable state before proposing
  3. wait for exact user message: approved
  4. approve --slug ... --intent ... --criteria ... [--lessons ...]
                                       merge lessons and persist the approved proposal before execution
  5. record --do ... --validate ... --retro ... --next-steps ... --recommendation ...
                                       record execution evidence, goal-progress reflection, and improvement actions
  6. gate                              lint, then run built-in context for the approval gate

Invariants:
  - never execute a proposed step before approve succeeds
  - approve requires a unique slug and a complete current step when one exists
  - mutate STEP state only through this CLI
  - proposed next steps are chat-only until exact approval
  - recommendation is null or one slug listed in next_steps
"""
TOP_FIELD_ORDER = ["goal", "lessons", "steps"]


class StepCliError(Exception):
    def __init__(self, message: str, code: int = EXIT_SCHEMA) -> None:
        super().__init__(message)
        self.code = code


class StepArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        raise StepCliError(message, EXIT_USAGE)


def emit(obj: Any) -> None:
    print(yaml.safe_dump(obj, sort_keys=False, allow_unicode=True), end="")


def normalize_match(value: str) -> str:
    lowered = value.lower()
    return "".join(ch for ch in lowered if not unicodedata.category(ch).startswith("P"))


def dedupe_normalized(values: list[Any]) -> tuple[list[str], bool]:
    seen: set[str] = set()
    out: list[str] = []
    changed = False
    for item in values:
        text = str(item)
        key = normalize_match(text)
        if key in seen:
            changed = True
            continue
        seen.add(key)
        out.append(text)
    return out, changed


def dedupe_slugs(values: list[Any]) -> tuple[list[str], bool]:
    seen: set[str] = set()
    out: list[str] = []
    changed = False
    for item in values:
        text = str(item).strip()
        if text in seen:
            changed = True
            continue
        seen.add(text)
        out.append(text)
    return out, changed


def parse_yaml_value(value: str) -> Any:
    raw = sys.stdin.read() if value == "-" else value
    try:
        return yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise StepCliError(f"failed to parse YAML value: {exc}", EXIT_SCHEMA) from exc


def ensure_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise StepCliError(f"{name} must be a YAML mapping/object")
    return value


def ensure_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise StepCliError(f"{name} must be a YAML list")
    return value


def resolve_file(args: argparse.Namespace, *, for_init: bool = False) -> Path:
    file_value = args.file or os.environ.get("STEP_FILE")
    if not file_value:
        raise StepCliError("provide --file STEP-<slug>.yaml or set STEP_FILE", EXIT_FILE)
    path = Path(file_value)
    if not for_init and not path.exists():
        raise StepCliError(f"step file does not exist: {path}", EXIT_FILE)
    return path


def read_step_file(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text())
    except OSError as exc:
        raise StepCliError(f"failed to read {path}: {exc}", EXIT_FILE) from exc
    except yaml.YAMLError as exc:
        raise StepCliError(f"failed to parse {path}: {exc}", EXIT_SCHEMA) from exc
    if not isinstance(data, dict):
        raise StepCliError("step file must contain a top-level mapping")
    return data


def ordered_step(step: dict[str, Any]) -> dict[str, Any]:
    ordered: dict[str, Any] = {}
    for key in STEP_FIELD_ORDER:
        if key in step:
            ordered[key] = step[key]
    for key, value in step.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def normalize_document(data: dict[str, Any]) -> dict[str, Any]:
    if isinstance(data.get("lessons"), list):
        data["lessons"], _ = dedupe_normalized(data["lessons"])
    if isinstance(data.get("steps"), list):
        for i, step in enumerate(data["steps"]):
            if not isinstance(step, dict):
                continue
            if isinstance(step.get("next_steps"), list):
                step["next_steps"], _ = dedupe_slugs(step["next_steps"])
            retro = step.get("retro")
            if isinstance(retro, dict):
                for key in ("wins", "issues", "actions"):
                    if isinstance(retro.get(key), list):
                        retro[key], _ = dedupe_normalized(retro[key])
            data["steps"][i] = ordered_step(step)
    ordered: dict[str, Any] = {}
    for key in TOP_FIELD_ORDER:
        if key in data:
            ordered[key] = data[key]
    for key, value in data.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def write_step_file(
    path: Path,
    data: dict[str, Any],
    *,
    create_parent: bool = False,
    dry_run: bool = False,
) -> None:
    if dry_run:
        normalize_document(data)
        return
    if create_parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    data = normalize_document(data)
    try:
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    except OSError as exc:
        raise StepCliError(f"failed to write {path}: {exc}", EXIT_FILE) from exc


def current_step(data: dict[str, Any]) -> dict[str, Any]:
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        raise StepCliError("step file has no current step")
    step = steps[-1]
    if not isinstance(step, dict):
        raise StepCliError("current step must be a mapping/object")
    return step


def current_step_or_none(data: dict[str, Any]) -> dict[str, Any] | None:
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        return None
    step = steps[-1]
    if not isinstance(step, dict):
        raise StepCliError("current step must be a mapping/object")
    return step


def result(args: argparse.Namespace, changed: bool, **extra: Any) -> dict[str, Any]:
    payload = {
        "ok": True,
        "file": str(resolve_file(args)),
        "operation": args.operation,
        "resource": args.resource,
        "changed": changed,
        "dry_run": args.dry_run,
    }
    payload.update(extra)
    return payload


def command_start(args: argparse.Namespace) -> int:
    path = resolve_file(args, for_init=True)
    if path.exists():
        if not args.force:
            emit({
                "ok": True,
                "file": str(path),
                "operation": "start",
                "resource": "step",
                "changed": False,
                "dry_run": args.dry_run,
            })
            return EXIT_OK
        data = read_step_file(path)
        changed = data.get("goal") != args.goal
        data["goal"] = args.goal
        if changed:
            write_step_file(path, data, dry_run=args.dry_run)
    else:
        lessons, _ = dedupe_normalized(args.lesson or [])
        data = {"goal": args.goal, "lessons": lessons, "steps": []}
        changed = True
        write_step_file(path, data, create_parent=True, dry_run=args.dry_run)
    emit({
        "ok": True,
        "file": str(path),
        "operation": "start",
        "resource": "step",
        "changed": changed,
        "dry_run": args.dry_run,
    })
    return EXIT_OK


def validate_slug(value: Any, label: str) -> None:
    if not isinstance(value, str) or not SLUG_RE.match(value):
        raise StepCliError(f"{label} must be lowercase kebab-case matching {SLUG_RE.pattern}")


def coerce_string_list(value: Any, name: str) -> list[str]:
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = [str(item) for item in value]
    else:
        raise StepCliError(f"{name} must be a string or list of strings")
    out = [str(item).strip() for item in values]
    if not out or any(not item for item in out):
        raise StepCliError(f"{name} must contain at least one non-empty string")
    return out


def parse_criteria_value(raw: str) -> Any:
    if raw == "-":
        return parse_yaml_value(raw)
    try:
        parsed = yaml.safe_load(raw)
    except yaml.YAMLError:
        return raw
    return parsed if isinstance(parsed, list) else raw


def collect_criteria(args: argparse.Namespace) -> list[str]:
    criteria: list[str] = []
    for raw in args.criteria or []:
        criteria.extend(coerce_string_list(parse_criteria_value(raw), "criteria"))
    if not criteria:
        raise StepCliError("append step requires --criteria")
    return criteria


def collect_optional_lessons(raw_values: list[str] | None) -> list[str]:
    lessons: list[str] = []
    for raw in raw_values or []:
        lessons.extend(coerce_string_list(parse_yaml_value(raw), "lessons"))
    return lessons


def coerce_slug_list(value: Any, name: str) -> list[str]:
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = [str(item) for item in value]
    else:
        raise StepCliError(f"{name} must be a slug string or list of slug strings")
    for slug in values:
        validate_slug(slug.strip(), name)
    return [slug.strip() for slug in values]


def coerce_recommendation(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise StepCliError("recommendation must be null or a slug string")
    slug = value.strip()
    validate_slug(slug, "recommendation")
    return slug


def merge_retro(step: dict[str, Any], value: dict[str, Any]) -> bool:
    had_retro = "retro" in step
    retro = step.setdefault("retro", {})
    if not isinstance(retro, dict):
        raise StepCliError("current.retro must be a mapping/object")
    changed = not had_retro
    for key in ("wins", "issues", "actions"):
        if key not in value:
            continue
        incoming = ensure_list(value[key], f"retro.{key}")
        current = retro.setdefault(key, [])
        if not isinstance(current, list):
            raise StepCliError(f"current.retro.{key} must be a list")
        before = list(current)
        retro[key], _ = dedupe_normalized(current + incoming)
        changed = changed or before != retro[key]
    return changed


def lint_basic(data: dict[str, Any], errors: list[str]) -> None:
    if not isinstance(data.get("goal"), str) or not data.get("goal"):
        errors.append("goal must be a non-empty string")
    lessons = data.get("lessons", [])
    if not isinstance(data.get("lessons"), list) or not all(
        isinstance(x, str) for x in lessons
    ):
        errors.append("lessons must be a list of strings")
    steps = data.get("steps")
    if not isinstance(steps, list):
        errors.append("steps must be a list")
        return
    if not steps:
        return
    seen: set[str] = set()
    for idx, step in enumerate(steps):
        if not isinstance(step, dict):
            errors.append(f"steps[{idx}] must be a mapping/object")
            continue
        slug = step.get("slug")
        if not isinstance(slug, str) or not SLUG_RE.match(slug):
            errors.append(f"steps[{idx}].slug must be lowercase kebab-case")
        elif slug in seen:
            errors.append(f"steps[{idx}].slug duplicates an earlier step slug: {slug}")
        else:
            seen.add(slug)
    current = steps[-1]
    if isinstance(current, dict):
        if not isinstance(current.get("slug"), str) or not current.get("slug"):
            errors.append("current_step.slug is required")
        if not isinstance(current.get("intent"), str) or not current.get("intent"):
            errors.append("current_step.intent is required")


def lint_step(step: Any, label: str, errors: list[str]) -> None:
    if not isinstance(step, dict):
        errors.append(f"{label} must be a mapping/object")
        return
    for key in ("slug", "intent"):
        if not isinstance(step.get(key), str) or not step.get(key):
            errors.append(f"{label}.{key} is required")
    criteria = step.get("criteria")
    if not isinstance(criteria, list) or not criteria or not all(isinstance(x, str) and x for x in criteria):
        errors.append(f"{label}.criteria must be a non-empty list of strings")
    if isinstance(step.get("slug"), str) and not SLUG_RE.match(step["slug"]):
        errors.append(f"{label}.slug must be lowercase kebab-case")
    do = step.get("do")
    if not isinstance(do, dict):
        errors.append(f"{label}.do must be a mapping/object")
    else:
        if not isinstance(do.get("summary"), str) or not do.get("summary"):
            errors.append(f"{label}.do.summary is required")
        if not isinstance(do.get("evidence"), list) or not all(isinstance(x, str) and x for x in do.get("evidence", [])):
            errors.append(f"{label}.do.evidence must be a list of non-empty strings")
    val = step.get("validate")
    if not isinstance(val, dict):
        errors.append(f"{label}.validate must be a mapping/object")
    else:
        if val.get("result") not in {"success", "partial", "failure"}:
            errors.append(f"{label}.validate.result must be success, partial, or failure")
        if not isinstance(val.get("evidence"), list) or not all(isinstance(x, str) and x for x in val.get("evidence", [])):
            errors.append(f"{label}.validate.evidence must be a list of non-empty strings")
    retro = step.get("retro")
    if not isinstance(retro, dict):
        errors.append(f"{label}.retro must be a mapping/object")
    else:
        for key in ("wins", "issues", "actions"):
            if not isinstance(retro.get(key), list):
                errors.append(f"{label}.retro.{key} must be a list")
    next_steps = step.get("next_steps")
    if not isinstance(next_steps, list) or not all(isinstance(x, str) for x in next_steps):
        errors.append(f"{label}.next_steps must be a list of strings")
        next_steps = []
    else:
        for slug in next_steps:
            if not SLUG_RE.match(slug):
                errors.append(f"{label}.next_steps contains invalid slug: {slug}")
    rec = step.get("recommendation")
    if rec is None:
        return
    if not isinstance(rec, str):
        errors.append(f"{label}.recommendation must be a slug string or null")
    else:
        if not SLUG_RE.match(rec):
            errors.append(f"{label}.recommendation must be lowercase kebab-case")
        if isinstance(next_steps, list) and rec not in next_steps:
            errors.append(f"{label}.recommendation is not listed in {label}.next_steps")


def lint_document(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    lint_basic(data, errors)
    steps = data.get("steps")
    if not isinstance(steps, list):
        return errors
    if not steps:
        errors.append("current_step is required")
        return errors
    for idx, step in enumerate(steps):
        lint_step(step, f"steps[{idx}]", errors)
    return errors


def command_lint(args: argparse.Namespace) -> int:
    errors = lint_document(read_step_file(resolve_file(args)))
    emit({"ok": not errors, "errors": errors, "dry_run": args.dry_run})
    return EXIT_OK if not errors else EXIT_LINT


def context_payload(data: dict[str, Any]) -> dict[str, Any]:
    """Return the complete resumable context used by context and gate."""
    return {
        "goal": data.get("goal"),
        "lessons": data.get("lessons", []),
        "current_step": current_step_or_none(data),
    }


def read_context(args: argparse.Namespace) -> dict[str, Any]:
    """Read the same resumable context used by context and gate."""
    return context_payload(read_step_file(resolve_file(args)))


def command_context(args: argparse.Namespace) -> int:
    emit(read_context(args))
    return EXIT_OK


def command_approve(args: argparse.Namespace) -> int:
    path = resolve_file(args)
    data = read_step_file(path)
    validate_slug(args.slug, "slug")
    criteria = collect_criteria(args)
    lesson_values = collect_optional_lessons(args.lessons)
    steps = data.setdefault("steps", [])
    if not isinstance(steps, list):
        raise StepCliError("steps must be a list")
    existing = [s.get("slug") for s in steps if isinstance(s, dict)]
    if args.slug in existing:
        raise StepCliError(
            f"approved slug already exists: {args.slug}; revise the proposal and request approval again"
        )
    if steps:
        prev = current_step(data)
        errors: list[str] = []
        warnings: list[str] = []
        lint_step(prev, "current_step", errors)
        if errors:
            raise StepCliError(
                "cannot approve a new step until the current step is complete: "
                + "; ".join(errors)
            )
        next_steps = prev.get("next_steps", [])
        if isinstance(next_steps, list) and args.slug not in next_steps:
            raise StepCliError(
                f"approved slug is not listed in current_step.next_steps: {args.slug}"
            )
    if lesson_values:
        lessons = data.setdefault("lessons", [])
        if not isinstance(lessons, list):
            raise StepCliError("lessons must be a list")
        lessons.extend(lesson_values)
        data["lessons"], _ = dedupe_normalized(lessons)
    steps.append({"slug": args.slug, "intent": args.intent, "criteria": criteria})
    write_step_file(path, data, dry_run=args.dry_run)
    emit({
        "ok": True,
        "file": str(path),
        "operation": "approve",
        "resource": "step",
        "changed": True,
        "dry_run": args.dry_run,
        "slug": args.slug,
        "lessons_added": len(lesson_values),
    })
    return EXIT_OK


def command_record(args: argparse.Namespace) -> int:
    path = resolve_file(args)
    data = read_step_file(path)
    step = current_step(data)
    changed = False
    supplied = [args.criteria, args.do, args.validate, args.retro, args.next_steps, args.recommendation]
    if not any(value is not None for value in supplied):
        raise StepCliError(
            "record requires at least one of --criteria, --do, --validate, --retro, --next-steps, or --recommendation",
            EXIT_USAGE,
        )
    if args.criteria is not None:
        value = collect_criteria(args)
        old = step.get("criteria")
        step["criteria"] = value
        changed = changed or old != value
    if args.do is not None:
        value = ensure_mapping(parse_yaml_value(args.do), "do")
        old = step.get("do")
        step["do"] = value
        changed = changed or old != value
    if args.validate is not None:
        value = ensure_mapping(parse_yaml_value(args.validate), "validate")
        old = step.get("validate")
        step["validate"] = value
        changed = changed or old != value
    if args.retro is not None:
        changed = merge_retro(step, ensure_mapping(parse_yaml_value(args.retro), "retro")) or changed
    if args.next_steps is not None:
        value, _ = dedupe_slugs(coerce_slug_list(parse_yaml_value(args.next_steps), "next_steps"))
        old = step.get("next_steps")
        step["next_steps"] = value
        changed = changed or old != value
    if args.recommendation is not None:
        value = coerce_recommendation(parse_yaml_value(args.recommendation))
        old = step.get("recommendation")
        step["recommendation"] = value
        changed = changed or old != value
    rec = step.get("recommendation")
    next_steps = step.get("next_steps", [])
    if isinstance(rec, str) and isinstance(next_steps, list) and rec not in next_steps:
        raise StepCliError("recommendation is not listed in current_step.next_steps")
    if changed:
        write_step_file(path, data, dry_run=args.dry_run)
    emit(result(args, changed))
    return EXIT_OK


def command_gate(args: argparse.Namespace) -> int:
    data = read_step_file(resolve_file(args))
    errors = lint_document(data)
    if errors:
        emit({"ok": False, "errors": errors})
        return EXIT_LINT
    # A successful gate runs the context read internally, so callers always receive
    # the same complete resumable state after validation.
    emit({"ok": True, **read_context(args)})
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    desc = __doc__ or "STEP YAML helper"
    parser = StepArgumentParser(
        description=desc,
        epilog=PROTOCOL_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--file", help="STEP-<slug>.yaml path; defaults to STEP_FILE env var")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="preview mutating operations without writing files",
    )
    parser.add_argument("--test", action="store_true", help="run the unittest self-test harness")
    sub = parser.add_subparsers(
        dest="operation",
        required=False,
        parser_class=StepArgumentParser,
    )

    p_start = sub.add_parser("start", help="protocol: create a new STEP file")
    p_start.add_argument(
        "--goal",
        required=True,
        help="workflow objective in concise prose",
    )
    p_start.add_argument("--lesson", action="append", help="initial lesson; may be repeated")
    p_start.add_argument(
        "--force",
        action="store_true",
        help="replace the goal of an existing workflow while preserving lessons and steps",
    )
    p_start.set_defaults(func=command_start, resource="step")

    p_context = sub.add_parser("context", help="protocol: show resumable context")
    p_context.set_defaults(func=command_context, resource="continuation")

    p_approve = sub.add_parser("approve", help="protocol: merge lessons and persist the exactly-approved proposal")
    p_approve.add_argument(
        "--slug",
        required=True,
        help="unique kebab-case identifier for the approved step",
    )
    p_approve.add_argument(
        "--intent",
        required=True,
        help="approved step objective in concise prose",
    )
    p_approve.add_argument("--criteria", action="append", required=True, help="criteria string, YAML list, or '-' for stdin; may repeat")
    p_approve.add_argument("--lessons", action="append", help="lesson string, YAML list, or '-' for stdin; may repeat; merged into top-level lessons")
    p_approve.set_defaults(func=command_approve, resource="step")

    p_record = sub.add_parser("record", help="protocol: record results, goal-progress retro, and next choices")
    p_record.add_argument("--criteria", action="append", help="criteria string, YAML list, or '-' for stdin; may repeat")
    p_record.add_argument("--do", dest="do", help="YAML object or '-' for stdin")
    p_record.add_argument("--validate", dest="validate", help="YAML object or '-' for stdin")
    p_record.add_argument("--retro", help="YAML object or '-' for stdin")
    p_record.add_argument("--next-steps", dest="next_steps", help="YAML slug/list or '-' for stdin")
    p_record.add_argument("--recommendation", help="YAML null or slug string")
    p_record.set_defaults(func=command_record, resource="current")

    p_gate = sub.add_parser("gate", help="protocol: lint, then run built-in context for the approval gate")
    p_gate.set_defaults(func=command_gate, resource="continuation")

    p_lint = sub.add_parser("lint", help="validate the complete workflow state")
    p_lint.set_defaults(func=command_lint, resource="step")
    return parser


def validate_args(args: argparse.Namespace) -> None:
    if args.test:
        return
    if args.operation is None:
        raise StepCliError("operation is required unless --test is supplied", EXIT_USAGE)


class StepCliSelfTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.step_file = Path(self.tmp.name) / "STEP-self-test.yaml"
        self.script = Path(__file__)

    def run_cli(self, *args: str, expect: int = EXIT_OK) -> subprocess.CompletedProcess[str]:
        cmd = [sys.executable, str(self.script), "--file", str(self.step_file), *args]
        proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
        self.assertEqual(proc.returncode, expect, msg=proc.stderr + proc.stdout)
        return proc

    def test_no_args_prints_help(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(self.script)], text=True, capture_output=True, check=False
        )
        self.assertEqual(proc.returncode, EXIT_OK)
        self.assertIn("Primary protocol commands:", proc.stdout)
        self.assertIn("goal-progress reflection, and improvement actions", proc.stdout)
        self.assertNotIn("operation is required unless --test is supplied", proc.stderr)

    def test_required_option_help_explains_inputs(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(self.script), "approve", "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, EXIT_OK)
        self.assertIn("unique kebab-case identifier", proc.stdout)
        self.assertIn("approved step objective", proc.stdout)

    def approve_first(self) -> None:
        self.run_cli(
            "approve", "--slug", "first-step", "--intent", "Do first",
            "--criteria", "First criterion",
        )

    def record_complete(self, *, next_steps: str = "[]", recommendation: str = "null") -> None:
        self.run_cli(
            "record",
            "--do", '{summary: "Did", evidence: ["file"]}',
            "--validate", '{result: success, evidence: ["checked"]}',
            "--retro", '{wins: [], issues: [], actions: []}',
            "--next-steps", next_steps,
            "--recommendation", recommendation,
        )

    def test_start_context_and_lint(self) -> None:
        self.run_cli("start", "--goal", "Goal")
        context = yaml.safe_load(self.run_cli("context").stdout)
        self.assertEqual(context["goal"], "Goal")
        self.assertIsNone(context["current_step"])
        linted = yaml.safe_load(self.run_cli("lint", expect=EXIT_LINT).stdout)
        self.assertIn("current_step is required", linted["errors"])

    def test_start_force_replaces_only_goal(self) -> None:
        self.run_cli("start", "--goal", "Old goal", "--lesson", "Keep lessons concise")
        self.approve_first()
        self.record_complete(next_steps="[second-step]", recommendation="second-step")
        self.run_cli("start", "--goal", "New goal", "--force")
        context = yaml.safe_load(self.run_cli("context").stdout)
        self.assertEqual(context["goal"], "New goal")
        self.assertEqual(context["lessons"], ["Keep lessons concise"])
        self.assertEqual(context["current_step"]["slug"], "first-step")

    def test_protocol_happy_path_and_lint(self) -> None:
        self.run_cli("start", "--goal", "Goal")
        self.approve_first()
        self.record_complete(next_steps="[second-step]", recommendation="second-step")
        context = yaml.safe_load(self.run_cli("context").stdout)
        gated = yaml.safe_load(self.run_cli("gate").stdout)
        linted = yaml.safe_load(self.run_cli("lint").stdout)
        self.assertTrue(gated["ok"])
        self.assertEqual(
            {key: value for key, value in gated.items() if key != "ok"}, context
        )
        self.assertEqual(gated["current_step"]["do"]["summary"], "Did")
        self.assertEqual(gated["current_step"]["validate"]["result"], "success")
        self.assertEqual(gated["current_step"]["next_steps"], ["second-step"])
        self.assertTrue(linted["ok"])

    def test_approve_merges_lessons(self) -> None:
        self.run_cli("start", "--goal", "Goal", "--lesson", "Keep lessons concise")
        self.run_cli(
            "approve", "--slug", "first-step", "--intent", "Do first",
            "--criteria", "First criterion",
            "--lessons", '[Keep lessons concise!, Prefer approval gates]',
        )
        context = yaml.safe_load(self.run_cli("context").stdout)
        self.assertEqual(context["lessons"], ["Keep lessons concise", "Prefer approval gates"])

    def test_record_rejects_unlisted_recommendation_before_write(self) -> None:
        self.run_cli("start", "--goal", "Goal")
        self.approve_first()
        proc = self.run_cli(
            "record", "--next-steps", "[second-step]", "--recommendation", "third-step",
            expect=EXIT_SCHEMA,
        )
        self.assertIn("recommendation is not listed", proc.stderr)
        current = yaml.safe_load(self.run_cli("context").stdout)["current_step"]
        self.assertNotIn("next_steps", current)
        self.assertNotIn("recommendation", current)

    def test_approve_rejects_duplicate_slug(self) -> None:
        self.run_cli("start", "--goal", "Goal")
        self.approve_first()
        self.record_complete(next_steps="[first-step]", recommendation="first-step")
        proc = self.run_cli(
            "approve", "--slug", "first-step", "--intent", "Repeat",
            "--criteria", "Repeat criterion", expect=EXIT_SCHEMA,
        )
        self.assertIn("approved slug already exists", proc.stderr)

    def test_terminal_gate_can_add_a_revised_next_choice(self) -> None:
        self.run_cli("start", "--goal", "Goal")
        self.approve_first()
        self.record_complete()
        terminal = yaml.safe_load(self.run_cli("gate").stdout)
        self.assertEqual(terminal["current_step"]["next_steps"], [])
        self.run_cli(
            "record", "--next-steps", "[second-step]", "--recommendation", "second-step",
        )
        revised = yaml.safe_load(self.run_cli("gate").stdout)
        self.assertEqual(revised["current_step"]["next_steps"], ["second-step"])
        self.run_cli(
            "approve", "--slug", "second-step", "--intent", "Do second",
            "--criteria", "Second criterion",
        )

    def test_dry_run_does_not_write(self) -> None:
        self.run_cli("start", "--goal", "Goal")
        self.run_cli("--dry-run", "start", "--goal", "New goal", "--force")
        context = yaml.safe_load(self.run_cli("context").stdout)
        self.assertEqual(context["goal"], "Goal")

def run_self_tests() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(StepCliSelfTest)
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    emit({"ok": result.wasSuccessful(), "tests": result.testsRun})
    return EXIT_OK if result.wasSuccessful() else EXIT_USAGE


def main() -> int:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    parser = build_parser()
    try:
        args = parser.parse_args()
        if args.operation is None and not args.test:
            parser.print_help()
            return EXIT_OK
        if yaml is None:
            log.error("PyYAML is required; install it with `pip install PyYAML`")
            return EXIT_SCHEMA
        validate_args(args)
        if args.test:
            return run_self_tests()
        return args.func(args)
    except StepCliError as exc:
        log.error(str(exc))
        return exc.code
    except BrokenPipeError:
        return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
