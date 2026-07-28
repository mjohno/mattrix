#!/usr/bin/env python3
"""
Validate MKF concept frontmatter.

Examples:
    python validate_frontmatter.py concept.md
    python validate_frontmatter.py --json concept.md another.md
    python validate_frontmatter.py --log-level DEBUG concept.md
    python validate_frontmatter.py --test

Stdout is reserved for JSON result data when --json is used. Human-readable
validation diagnostics, warnings, and logs go to stderr.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

REQUIRED = ("type", "title", "description", "tags")
KNOWN = set(REQUIRED) | {"resource", "generated_by"}
REQUIRED_HINT = "required MKF frontmatter fields are: type, title, description, tags"


def parse_simple_yaml(raw: str) -> dict[str, Any]:
    """Parse the small YAML subset used by MKF frontmatter."""
    data: dict[str, Any] = {}
    current_key = None
    for line_no, line in enumerate(raw.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and current_key:
            data.setdefault(current_key, [])
            if not isinstance(data[current_key], list):
                raise ValueError(f"line {line_no}: cannot append list item to scalar {current_key}")
            data[current_key].append(line[4:].strip().strip('"\''))
            continue
        if ":" not in line:
            raise ValueError(f"line {line_no}: expected key: value")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"line {line_no}: empty key")
        current_key = key
        if value == "":
            data[key] = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [] if not inner else [
                item.strip().strip('"\'') for item in inner.split(",")
            ]
        elif value.lower() in {"true", "false"}:
            data[key] = value.lower() == "true"
        else:
            data[key] = value.strip('"\'')
    return data


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split a Markdown document into parsed YAML frontmatter and body."""
    if not text.startswith("---\n"):
        raise ValueError(f"missing YAML frontmatter opening delimiter; {REQUIRED_HINT}")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("missing YAML frontmatter closing delimiter '---'")
    raw = text[4:end].strip("\n")
    return parse_simple_yaml(raw), text[end + len("\n---") :]


def validate(path: Path) -> dict[str, Any]:
    """Validate one MKF concept path and return a structured result."""
    errors: list[str] = []
    warnings: list[str] = []
    frontmatter: dict[str, Any] = {}

    try:
        text = path.read_text(encoding="utf-8")
        frontmatter, _ = split_frontmatter(text)
    except Exception as exc:  # noqa: BLE001 - validator returns user-facing parse errors.
        errors.append(str(exc))

    if frontmatter:
        for key in REQUIRED:
            if key not in frontmatter:
                errors.append(f"missing required field: {key}; {REQUIRED_HINT}")
            elif (
                key != "tags"
                and (frontmatter[key] is None or str(frontmatter[key]).strip() == "")
            ):
                errors.append(f"required field is empty: {key}; provide a non-empty value")
        tags = frontmatter.get("tags")
        if "tags" in frontmatter and not isinstance(tags, list):
            errors.append("tags must be a YAML list; use tags: [] when there are no tags")
        for key in frontmatter:
            if key not in KNOWN:
                warnings.append(f"unknown frontmatter key preserved: {key}")
        if "timestamp" in frontmatter:
            warnings.append("timestamp is not required by MKF and should not be auto-maintained")

    return {
        "path": str(path),
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "frontmatter": frontmatter,
    }


def emit_human_results(results: list[dict[str, Any]]) -> None:
    """Write human-readable validation diagnostics to stderr."""
    for result in results:
        status = "valid" if result["valid"] else "invalid"
        print(f"{status}: {result['path']}", file=sys.stderr)
        for error in result["errors"]:
            print(f"  error: {error}", file=sys.stderr)
        for warning in result["warnings"]:
            print(f"  warning: {warning}", file=sys.stderr)


def configure_logging(log_level: str) -> None:
    """Configure diagnostic logging to stderr."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s [%(levelname)s] [%(funcName)s]: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stderr,
        force=True,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Validate MKF concept frontmatter.")
    parser.add_argument("paths", nargs="*", help="Markdown concept paths to validate")
    parser.add_argument("--json", action="store_true", help="Emit JSON output to stdout")
    parser.add_argument(
        "--log-level",
        default="CRITICAL",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: CRITICAL)",
    )
    parser.add_argument("--test", action="store_true", help="Run inline tests")
    args = parser.parse_args(argv)
    if not args.test and not args.paths:
        parser.error("at least one path is required unless --test is used")
    return args


def main(args: argparse.Namespace) -> int:
    """Run frontmatter validation and return an exit code."""
    results = [validate(Path(path).expanduser()) for path in args.paths]
    ok = all(result["valid"] for result in results)

    if args.json:
        print(json.dumps({"valid": ok, "results": results}, indent=2, ensure_ascii=False))
    else:
        emit_human_results(results)
    return 0 if ok else 1


def run_tests() -> int:
    """Run inline tests using unittest. Return 0 if all pass, 1 if any fail."""

    class TestValidateFrontmatter(unittest.TestCase):
        def test_parse_args(self) -> None:
            parsed = parse_args(["--json", "concept.md", "--log-level", "DEBUG"])
            self.assertTrue(parsed.json)
            self.assertEqual(parsed.paths, ["concept.md"])
            self.assertEqual(parsed.log_level, "DEBUG")
            self.assertTrue(parse_args(["--test"]).test)
            with self.assertRaises(SystemExit):
                parse_args([])

        def test_valid_concept(self) -> None:
            with tempfile.TemporaryDirectory() as temp_dir:
                path = Path(temp_dir) / "concept.md"
                path.write_text(
                    "---\n"
                    "type: undefined\n"
                    "title: Valid\n"
                    "description: Valid concept.\n"
                    "tags: []\n"
                    "---\n\nBody\n",
                    encoding="utf-8",
                )
                result = validate(path)
                self.assertTrue(result["valid"])

        def test_missing_required_field(self) -> None:
            with tempfile.TemporaryDirectory() as temp_dir:
                path = Path(temp_dir) / "bad.md"
                path.write_text("---\ntitle: Bad\n---\nBody\n", encoding="utf-8")
                result = validate(path)
                self.assertFalse(result["valid"])
                self.assertTrue(any("missing required field: type" in e for e in result["errors"]))

    suite = unittest.TestLoader().loadTestsFromTestCase(TestValidateFrontmatter)
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    cli_args = parse_args(sys.argv[1:])
    configure_logging(cli_args.log_level)
    if cli_args.test:
        sys.exit(run_tests())
    sys.exit(main(cli_args))
