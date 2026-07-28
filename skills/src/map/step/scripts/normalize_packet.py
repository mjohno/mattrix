#!/usr/bin/env python3
"""Build and validate a STEP role YAML packet without accessing STEP state."""
from __future__ import annotations
import argparse
import re
import sys
import unittest
from typing import Any
import yaml

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESULTS = {"success", "partial", "failure", "blocked"}
OUTCOMES = {"progressed", "partial", "blocked", "failed"}

class PacketError(ValueError): pass


def mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict): raise PacketError(f"{label} must be a mapping")
    return value


def strings(value: Any, label: str, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value): raise PacketError(f"{label} must be a list of non-empty strings")
    if nonempty and not value: raise PacketError(f"{label} must not be empty")
    return value


def task(value: Any, label: str = "packet", complete: bool = False) -> dict[str, Any]:
    obj = mapping(value, label)
    if not isinstance(obj.get("slug"), str) or not SLUG.fullmatch(obj["slug"]): raise PacketError(f"{label}.slug must be lowercase kebab-case")
    if not isinstance(obj.get("intent"), str) or not obj["intent"].strip(): raise PacketError(f"{label}.intent is required")
    strings(obj.get("criteria"), f"{label}.criteria", True)
    if complete:
        for field in ("do", "validate"):
            part = mapping(obj.get(field), f"{label}.{field}")
            strings(part.get("evidence"), f"{label}.{field}.evidence")
        if not isinstance(obj["do"].get("summary"), str) or not obj["do"]["summary"].strip(): raise PacketError(f"{label}.do.summary is required")
        if obj["validate"].get("result") not in RESULTS: raise PacketError(f"{label}.validate.result is invalid")
    return obj


def proposals(obj: dict[str, Any]) -> None:
    packets = obj.get("proposed_next_packets")
    if not isinstance(packets, list): raise PacketError("proposed_next_packets must be a list")
    slugs = [task(x, f"proposed_next_packets[{i}]")["slug"] for i, x in enumerate(packets)]
    if len(set(slugs)) != len(slugs): raise PacketError("proposed_next_packets contains duplicate slugs")
    rec = obj.get("recommendation")
    if rec is not None and rec not in slugs: raise PacketError("recommendation must name a proposed packet or be null")


def validate(role: str, obj: Any) -> dict[str, Any]:
    obj = mapping(obj, role)
    if role == "coordinator":
        strings(obj.get("lessons"), "lessons")
        proposals(obj)
    elif role == "worker": task(obj.get("packet"), "packet", True)
    elif role == "assessor":
        task(obj.get("current_packet"), "current_packet", True)
        if obj.get("outcome") not in OUTCOMES: raise PacketError("outcome is invalid")
        retro = mapping(obj.get("retro"), "retro")
        for key in ("wins", "issues", "actions"): strings(retro.get(key), f"retro.{key}")
        if not isinstance(obj.get("clarification_needed"), bool): raise PacketError("clarification_needed must be boolean")
    else: raise PacketError(f"unknown role: {role}")
    return obj


def repeated(parser: argparse.ArgumentParser, option: str, *, required: bool = False, help: str) -> None:
    parser.add_argument(option, action="append", default=[], required=required, metavar="TEXT", help=help)


def add_complete_task_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--slug", required=True, help="lowercase kebab-case task identifier")
    parser.add_argument("--intent", required=True, help="concise task outcome")
    repeated(parser, "--criteria", required=True, help="observable acceptance criterion; repeat for each criterion")
    parser.add_argument("--do-summary", required=True, help="summary of work performed")
    repeated(parser, "--do-evidence", help="work evidence; repeat for each item")
    parser.add_argument("--validate-result", choices=sorted(RESULTS), required=True, help="validation result")
    repeated(parser, "--validate-evidence", help="validation evidence; repeat for each item")


def complete_task_from(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "slug": args.slug,
        "intent": args.intent,
        "criteria": args.criteria,
        "do": {"summary": args.do_summary, "evidence": args.do_evidence},
        "validate": {"result": args.validate_result, "evidence": args.validate_evidence},
    }


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build and validate a STEP role YAML packet")
    p.add_argument("--test", action="store_true", help="run script-local packet tests")
    sub = p.add_subparsers(dest="role")

    coordinator = sub.add_parser("coordinator", help="build a coordinator packet")
    repeated(coordinator, "--lessons", help="durable lesson; repeat for each lesson")
    repeated(coordinator, "--slug", help="proposed task identifier; repeat this option for each proposal")
    repeated(coordinator, "--intent", help="proposed task outcome; repeat this option for each proposal")
    coordinator.add_argument("--criteria", action="append", nargs="+", default=[], metavar="TEXT", help="criteria for one proposal; repeat this option for each proposal")
    coordinator.add_argument("--recommendation", help="slug of the recommended proposal")

    worker = sub.add_parser("worker", help="build a worker packet")
    add_complete_task_options(worker)

    assessor = sub.add_parser("assessor", help="build an assessor packet")
    add_complete_task_options(assessor)
    assessor.add_argument("--outcome", choices=sorted(OUTCOMES), required=True, help="assessed workflow outcome")
    repeated(assessor, "--retro-wins", help="effective progress; repeat for each item")
    repeated(assessor, "--retro-issues", help="friction or failure; repeat for each item")
    repeated(assessor, "--retro-actions", help="concrete next-step input; repeat for each item")
    assessor.add_argument("--clarification-needed", action=argparse.BooleanOptionalAction, default=False, help="whether one worker clarification is needed")
    return p


def packet_from(args: argparse.Namespace) -> dict[str, Any]:
    if args.role == "coordinator":
        counts = (len(args.slug), len(args.intent), len(args.criteria))
        if len(set(counts)) != 1:
            raise PacketError("each proposal needs --slug, --intent, and --criteria")
        return {
            "lessons": args.lessons,
            "proposed_next_packets": [
                {"slug": slug, "intent": intent, "criteria": criteria}
                for slug, intent, criteria in zip(args.slug, args.intent, args.criteria)
            ],
            "recommendation": args.recommendation,
        }
    if args.role == "worker": return {"packet": complete_task_from(args)}
    if args.role == "assessor":
        return {
            "current_packet": complete_task_from(args),
            "outcome": args.outcome,
            "retro": {"wins": args.retro_wins, "issues": args.retro_issues, "actions": args.retro_actions},
            "clarification_needed": args.clarification_needed,
        }
    raise PacketError("select coordinator, worker, or assessor")


class NormalizerTests(unittest.TestCase):
    def test_valid_role_packets(self) -> None:
        coordinator = packet_from(parser().parse_args(["coordinator", "--lessons", "Keep evidence", "--slug", "next-task", "--intent", "Continue", "--criteria", "done", "--recommendation", "next-task"]))
        worker = packet_from(parser().parse_args(["worker", "--slug", "next-task", "--intent", "Continue", "--criteria", "done", "--do-summary", "Worked", "--validate-result", "success"]))
        assessor = packet_from(parser().parse_args(["assessor", "--slug", "next-task", "--intent", "Continue", "--criteria", "done", "--do-summary", "Worked", "--validate-result", "success", "--outcome", "progressed", "--retro-wins", "work", "--retro-actions", "continue"]))
        for role, packet in (("coordinator", coordinator), ("worker", worker), ("assessor", assessor)):
            self.assertEqual(validate(role, packet), packet)

    def test_proposals_require_aligned_fields(self) -> None:
        args = parser().parse_args(["coordinator", "--slug", "next-task"])
        with self.assertRaises(PacketError): packet_from(args)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.test:
        result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(NormalizerTests))
        return 0 if result.wasSuccessful() else 1
    try:
        print(yaml.safe_dump(validate(args.role, packet_from(args)), sort_keys=False), end="")
    except PacketError as exc:
        print(f"packet error: {exc}", file=sys.stderr); return 2
    return 0


if __name__ == "__main__": raise SystemExit(main())
