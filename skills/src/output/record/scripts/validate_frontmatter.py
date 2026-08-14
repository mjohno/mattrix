#!/usr/bin/env python3
"""Validate MKF/OKF v0.2 concept frontmatter."""
from __future__ import annotations

import argparse
import json
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised at process startup
    print(
        "warning: PyYAML is required to validate MKF concepts. Install PyYAML and rerun "
        "this record script.",
        file=sys.stderr,
    )
    sys.exit(2)

RESERVED = {"index.md", "log.md"}


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter opening delimiter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("missing YAML frontmatter closing delimiter '---'")
    try:
        data = yaml.safe_load(text[4:end].strip("\n"))
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML frontmatter: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    return data, text[end + len("\n---") :]


def validate(path: Path) -> dict[str, Any]:
    errors: list[str] = []
    frontmatter: dict[str, Any] = {}
    if path.name in RESERVED:
        errors.append(f"{path.name} is a reserved OKF file, not a concept")
    else:
        try:
            frontmatter, _ = split_frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
    if frontmatter:
        concept_type = frontmatter.get("type")
        if not isinstance(concept_type, str) or not concept_type.strip():
            errors.append("missing or empty required field: type")
    return {"path": str(path), "valid": not errors, "errors": errors, "frontmatter": frontmatter}


def emit_human_results(results: list[dict[str, Any]]) -> None:
    for result in results:
        print(f"{'valid' if result['valid'] else 'invalid'}: {result['path']}", file=sys.stderr)
        for error in result["errors"]:
            print(f"  error: {error}", file=sys.stderr)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate MKF/OKF v0.2 concept frontmatter.")
    parser.add_argument("paths", nargs="*", help="Markdown concept paths to validate")
    parser.add_argument("--json", action="store_true", help="Emit JSON output to stdout")
    parser.add_argument("--test", action="store_true", help="Run inline tests")
    args = parser.parse_args(argv)
    if not args.test and not args.paths:
        parser.error("at least one path is required unless --test is used")
    return args


def main(args: argparse.Namespace) -> int:
    results = [validate(Path(path).expanduser()) for path in args.paths]
    if args.json:
        print(json.dumps({"valid": all(r["valid"] for r in results), "results": results}, indent=2, ensure_ascii=False, default=str))
    else:
        emit_human_results(results)
    return 0 if all(r["valid"] for r in results) else 1


def run_tests() -> int:
    class TestValidateFrontmatter(unittest.TestCase):
        def test_type_only_concept_is_valid(self) -> None:
            with tempfile.TemporaryDirectory() as temp_dir:
                path = Path(temp_dir) / "concept.md"
                path.write_text("---\ntype: undefined\n---\nBody\n", encoding="utf-8")
                self.assertTrue(validate(path)["valid"])

        def test_nested_okf_metadata_is_preserved(self) -> None:
            with tempfile.TemporaryDirectory() as temp_dir:
                path = Path(temp_dir) / "concept.md"
                path.write_text("---\ntype: Metric\nsources:\n  - id: policy\n    resource: https://example.test/policy\ngenerated: { by: process:test, at: 2026-01-01T00:00:00Z }\nverified:\n  - by: human:reviewer\n    at: 2026-01-02T00:00:00Z\n---\n", encoding="utf-8")
                result = validate(path)
                self.assertTrue(result["valid"])
                self.assertEqual(result["frontmatter"]["sources"][0]["id"], "policy")

        def test_reserved_and_invalid_concepts_fail(self) -> None:
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                (root / "index.md").write_text("# Index\n", encoding="utf-8")
                (root / "bad.md").write_text("---\ntype: [\n---\n", encoding="utf-8")
                self.assertFalse(validate(root / "index.md")["valid"])
                self.assertFalse(validate(root / "bad.md")["valid"])
        def test_missing_pyyaml_reports_actionable_warning(self) -> None:
            result = subprocess.run([sys.executable, "-S", __file__, "--test"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("warning: PyYAML is required", result.stderr)
            self.assertIn("Install PyYAML and rerun", result.stderr)

    result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(unittest.TestLoader().loadTestsFromTestCase(TestValidateFrontmatter))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    sys.exit(run_tests() if args.test else main(args))
