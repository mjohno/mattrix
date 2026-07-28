#!/usr/bin/env python3
"""
Rebuild generated MKF index.md files for a bundle tree.

Examples:
    python rebuild_indexes.py /knowledge/general
    python rebuild_indexes.py --dry-run --json /knowledge/general
    python rebuild_indexes.py --force --log-level DEBUG /knowledge/general
    python rebuild_indexes.py --test

Stdout is reserved for JSON result data when --json is used. Human-readable
write/skip/error diagnostics and logs go to stderr.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Iterable

log = logging.getLogger(__name__)

GENERATOR = "mkf-rebuild-indexes"


def parse_simple_yaml(raw: str) -> dict[str, Any]:
    """Parse the small YAML subset used by MKF frontmatter."""
    data: dict[str, Any] = {}
    current_key = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and current_key:
            data.setdefault(current_key, [])
            if isinstance(data[current_key], list):
                data[current_key].append(line[4:].strip().strip('"\''))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if value == "":
            data[key] = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [] if not inner else [
                item.strip().strip('"\'') for item in inner.split(",")
            ]
        else:
            data[key] = value.strip('"\'')
    return data


def split_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    """Return parsed frontmatter and body, or empty data on read failure."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        log.warning("Could not read %s: %s", path, exc)
        return {}, ""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    return parse_simple_yaml(text[4:end].strip("\n")), text[end + len("\n---") :]


def titleize(name: str) -> str:
    """Convert a slug-like filename or directory name into a display title."""
    cleaned = re.sub(r"[-_]+", " ", name).strip()
    return cleaned.title() if cleaned else "Index"


def child_dirs(directory: Path) -> list[Path]:
    """Return non-hidden child directories in deterministic order."""
    return sorted(
        child
        for child in directory.iterdir()
        if child.is_dir() and not child.name.startswith(".")
    )


def child_concepts(directory: Path) -> list[Path]:
    """Return direct child Markdown concepts, excluding index.md."""
    concepts = [
        child
        for child in directory.iterdir()
        if child.is_file() and child.suffix == ".md" and child.name != "index.md"
    ]
    return sorted(concepts, key=lambda path: path.name)


def render_index(bundle_root: Path, directory: Path) -> str:
    """Render a generated MKF index concept for one bundle directory."""
    rel = directory.relative_to(bundle_root) if directory != bundle_root else Path("")
    title = titleize(bundle_root.name if directory == bundle_root else directory.name)
    description = (
        "Generated index for this MKF bundle."
        if directory == bundle_root
        else f"Generated index for {rel.as_posix()}."
    )

    lines = [
        "---",
        "type: index",
        f"title: {title}",
        f"description: {description}",
        "tags: []",
        f"generated_by: {GENERATOR}",
        "---",
        "",
        f"# {title}",
        "",
    ]

    dirs = child_dirs(directory)
    concepts = child_concepts(directory)

    if dirs:
        lines.extend(["## Subdirectories", ""])
        for child in dirs:
            lines.append(f"- [{titleize(child.name)}/]({child.name}/index.md)")
        lines.append("")

    if concepts:
        lines.extend(["## Concepts", ""])
        for concept in concepts:
            frontmatter, _ = split_frontmatter(concept)
            item_title = frontmatter.get("title") or titleize(concept.stem)
            description_text = frontmatter.get("description", "")
            suffix = f" — {description_text}" if description_text else ""
            lines.append(f"- [{item_title}]({concept.name}){suffix}")
        lines.append("")

    if not dirs and not concepts:
        lines.extend(["No child concepts or subdirectories found.", ""])

    return "\n".join(lines)


def all_directories(bundle_root: Path) -> Iterable[Path]:
    """Yield bundle directories in deterministic order, excluding hidden paths."""
    yield bundle_root
    for path in sorted(bundle_root.rglob("*")):
        rel_parts = path.relative_to(bundle_root).parts
        if path.is_dir() and not any(part.startswith(".") for part in rel_parts):
            yield path


def is_generated_index(index_path: Path) -> bool:
    """Return whether an existing index was generated by this script."""
    frontmatter, _ = split_frontmatter(index_path)
    return frontmatter.get("generated_by") == GENERATOR


def validate_index_text(text: str) -> list[str]:
    """Validate generated index text before writing it."""
    errors: list[str] = []
    if not text.startswith("---\n"):
        errors.append("missing frontmatter")
        return errors
    end = text.find("\n---", 4)
    if end == -1:
        errors.append("missing frontmatter close")
        return errors
    frontmatter = parse_simple_yaml(text[4:end].strip("\n"))
    for key in ("type", "title", "description", "tags"):
        if key not in frontmatter:
            errors.append(f"missing required field: {key}")
    if frontmatter.get("type") != "index":
        errors.append("generated index must use type: index")
    if not isinstance(frontmatter.get("tags"), list):
        errors.append("tags must be a list; use tags: [] when there are no tags")
    return errors


def rebuild(bundle_root: Path, force: bool = False, dry_run: bool = False) -> dict[str, Any]:
    """Rebuild or plan generated indexes for a bundle root."""
    written: list[str] = []
    would_write: list[str] = []
    skipped: list[dict[str, str]] = []
    errors: list[dict[str, Any]] = []

    for directory in all_directories(bundle_root):
        index_path = directory / "index.md"
        if index_path.exists() and not force and not is_generated_index(index_path):
            skipped.append(
                {
                    "path": str(index_path),
                    "reason": "existing non-generated index; rerun with --force to overwrite it",
                }
            )
            continue

        text = render_index(bundle_root, directory)
        validation_errors = validate_index_text(text)
        if validation_errors:
            errors.append({"path": str(index_path), "errors": validation_errors})
            continue

        if dry_run:
            would_write.append(str(index_path))
            log.info("Would write generated index: %s", index_path)
        else:
            index_path.write_text(text, encoding="utf-8")
            written.append(str(index_path))
            log.info("Wrote generated index: %s", index_path)

    return {
        "bundle_root": str(bundle_root),
        "dry_run": dry_run,
        "written": written,
        "would_write": would_write,
        "skipped": skipped,
        "errors": errors,
    }


def emit_human_result(result: dict[str, Any]) -> None:
    """Write human-readable rebuild results to stderr."""
    for path in result["would_write"]:
        print(f"would write: {path}", file=sys.stderr)
    for path in result["written"]:
        print(f"written: {path}", file=sys.stderr)
    for item in result["skipped"]:
        print(f"skipped: {item['path']} ({item['reason']})", file=sys.stderr)
    for item in result["errors"]:
        print(f"error: {item}", file=sys.stderr)


def missing_root_result(root: Path) -> dict[str, Any]:
    """Return a structured error for a missing bundle root."""
    return {
        "bundle_root": str(root),
        "dry_run": False,
        "written": [],
        "would_write": [],
        "skipped": [],
        "errors": [
            {
                "error": "bundle root not found; provide an existing MKF bundle directory path",
                "path": str(root),
            }
        ],
    }


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
    parser = argparse.ArgumentParser(
        description="Rebuild generated MKF index.md files for a bundle tree."
    )
    parser.add_argument("bundle_root", nargs="?", help="MKF bundle root")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing non-generated index.md files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show intended writes without modifying files",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output to stdout")
    parser.add_argument(
        "--log-level",
        default="CRITICAL",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: CRITICAL)",
    )
    parser.add_argument("--test", action="store_true", help="Run inline tests")
    args = parser.parse_args(argv)
    if not args.test and not args.bundle_root:
        parser.error("bundle_root is required unless --test is used")
    return args


def main(args: argparse.Namespace) -> int:
    """Run index rebuilding and return an exit code."""
    root = Path(args.bundle_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        result = missing_root_result(root)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            emit_human_result(result)
        return 2

    result = rebuild(root, force=args.force, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        emit_human_result(result)
    return 0 if not result["errors"] else 1


def run_tests() -> int:
    """Run inline tests using unittest. Return 0 if all pass, 1 if any fail."""

    class TestRebuildIndexes(unittest.TestCase):
        def test_parse_args(self) -> None:
            parsed = parse_args(["--dry-run", "/tmp/example", "--log-level", "DEBUG"])
            self.assertTrue(parsed.dry_run)
            self.assertEqual(parsed.bundle_root, "/tmp/example")
            self.assertEqual(parsed.log_level, "DEBUG")
            self.assertTrue(parse_args(["--test"]).test)
            with self.assertRaises(SystemExit):
                parse_args([])

        def test_dry_run_does_not_write(self) -> None:
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                concept = root / "concept.md"
                concept.write_text(
                    "---\n"
                    "type: undefined\n"
                    "title: Concept\n"
                    "description: Test concept.\n"
                    "tags: []\n"
                    "---\n\nBody\n",
                    encoding="utf-8",
                )
                result = rebuild(root, dry_run=True)
                self.assertEqual(result["written"], [])
                self.assertTrue(result["would_write"])
                self.assertFalse((root / "index.md").exists())

        def test_rebuild_writes_index(self) -> None:
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                (root / "concept.md").write_text(
                    "---\n"
                    "type: undefined\n"
                    "title: Concept\n"
                    "description: Test concept.\n"
                    "tags: []\n"
                    "---\n\nBody\n",
                    encoding="utf-8",
                )
                result = rebuild(root)
                self.assertFalse(result["errors"])
                self.assertTrue((root / "index.md").exists())

        def test_non_generated_index_is_skipped(self) -> None:
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                (root / "index.md").write_text("# Manual\n", encoding="utf-8")
                result = rebuild(root)
                self.assertTrue(result["skipped"])
                self.assertIn("--force", result["skipped"][0]["reason"])

    suite = unittest.TestLoader().loadTestsFromTestCase(TestRebuildIndexes)
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    cli_args = parse_args(sys.argv[1:])
    configure_logging(cli_args.log_level)
    if cli_args.test:
        sys.exit(run_tests())
    sys.exit(main(cli_args))
