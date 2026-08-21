#!/usr/bin/env python3
"""Explicitly rebuild OKF index.md files for a bundle tree."""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
import unittest
from collections.abc import Iterable
from pathlib import Path
from typing import Any

RESERVED = {"index.md", "log.md"}


def titleize(name: str) -> str:
    cleaned = re.sub(r"[-_]+", " ", name).strip()
    return cleaned.title() if cleaned else "Index"


def all_directories(bundle_root: Path) -> Iterable[Path]:
    """Yield each reachable directory once, following directory symlinks."""
    pending = [bundle_root]
    visited: set[Path] = set()
    while pending:
        directory = pending.pop()
        try:
            identity = directory.resolve(strict=True)
        except OSError as exc:
            raise OSError(
                f"cannot resolve directory {directory}: {exc}"
            ) from exc
        if identity in visited:
            continue
        visited.add(identity)
        yield directory
        try:
            children = sorted(directory.iterdir(), reverse=True)
        except OSError as exc:
            raise OSError(f"cannot read directory {directory}: {exc}") from exc
        pending.extend(
            child
            for child in children
            if child.is_dir() and not child.name.startswith(".")
        )


def render_index(bundle_root: Path, directory: Path) -> str:
    title = titleize(
        bundle_root.name if directory == bundle_root else directory.name
    )
    children = list(directory.iterdir())
    dirs = sorted(
        (
            child
            for child in children
            if child.is_dir() and not child.name.startswith(".")
        ),
        key=lambda path: path.name,
    )
    concepts = sorted(
        (
            child
            for child in children
            if child.is_file()
            and child.suffix == ".md"
            and child.name not in RESERVED
        ),
        key=lambda path: path.name,
    )
    lines = [f"# {title}", ""]
    if dirs:
        lines.extend(["## Subdirectories", ""])
        lines.extend(
            f"* [{titleize(child.name)}]({child.name}/)" for child in dirs
        )
        lines.append("")
    if concepts:
        lines.extend(["## Concepts", ""])
        lines.extend(
            f"* [{titleize(concept.stem)}]({concept.name})"
            for concept in concepts
        )
        lines.append("")
    if not dirs and not concepts:
        lines.extend(["No child concepts or subdirectories found.", ""])
    return "\n".join(lines)


def rebuild(bundle_root: Path, write: bool = False) -> dict[str, Any]:
    written: list[str] = []
    would_write: list[str] = []
    errors: list[dict[str, str]] = []
    planned: list[tuple[Path, str]] = []
    try:
        for directory in all_directories(bundle_root):
            text = render_index(bundle_root, directory)
            planned.append((directory / "index.md", text))
    except OSError as exc:
        errors.append({"path": str(bundle_root), "error": str(exc)})
    if errors:
        return {
            "bundle_root": str(bundle_root),
            "dry_run": not write,
            "written": written,
            "would_write": would_write,
            "errors": errors,
        }
    if not write:
        would_write = [str(path) for path, _ in planned]
    else:
        for path, text in planned:
            try:
                path.write_text(text, encoding="utf-8")
                written.append(str(path))
            except OSError as exc:
                errors.append(
                    {
                        "path": str(path),
                        "error": f"could not write index: {exc}",
                    }
                )
                break
    return {
        "bundle_root": str(bundle_root),
        "dry_run": not write,
        "written": written,
        "would_write": would_write,
        "errors": errors,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Explicitly rebuild OKF index.md files."
    )
    parser.add_argument("bundle_root", nargs="?", help="MKF bundle root")
    parser.add_argument(
        "--write", action="store_true", help="Write indexes; default is dry run"
    )
    parser.add_argument("--test", action="store_true", help="Run inline tests")
    args = parser.parse_args(argv)
    if not args.test and not args.bundle_root:
        parser.error("bundle_root is required unless --test is used")
    return args


def main(args: argparse.Namespace) -> int:
    root = Path(args.bundle_root).expanduser()
    if not root.is_dir():
        print(f"error: bundle root not found: {root}", file=sys.stderr)
        return 2
    result = rebuild(root, write=args.write)
    for path in result["would_write"]:
        print(f"would write: {path}", file=sys.stderr)
    for path in result["written"]:
        print(f"written: {path}", file=sys.stderr)
    for error in result["errors"]:
        print(f"error: {error['path']}: {error['error']}", file=sys.stderr)
    return 0 if not result["errors"] else 1


def run_tests() -> int:
    class TestRebuildIndexes(unittest.TestCase):
        def test_default_is_dry_run_and_write_overrides_index(self) -> None:
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                (root / "concept.md").write_text(
                    "---\ntype: undefined\n---\n", encoding="utf-8"
                )
                (root / "index.md").write_text("# Manual\n", encoding="utf-8")
                self.assertTrue(rebuild(root)["would_write"])
                self.assertFalse(rebuild(root, write=True)["errors"])
                self.assertIn(
                    "concept.md",
                    (root / "index.md").read_text(encoding="utf-8"),
                )

        def test_follows_symlink_once_and_excludes_log(self) -> None:
            with (
                tempfile.TemporaryDirectory() as temp_dir,
                tempfile.TemporaryDirectory() as linked_dir,
            ):
                root, linked = Path(temp_dir), Path(linked_dir)
                (linked / "concept.md").write_text(
                    "---\ntype: undefined\n---\n", encoding="utf-8"
                )
                (linked / "log.md").write_text("# Log\n", encoding="utf-8")
                (root / "linked").symlink_to(linked, target_is_directory=True)
                self.assertFalse(rebuild(root, write=True)["errors"])
                text = (linked / "index.md").read_text(encoding="utf-8")
                self.assertIn("concept.md", text)
                self.assertNotIn("log.md", text)
                self.assertNotIn("generated by", text)

    result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(
        unittest.TestLoader().loadTestsFromTestCase(TestRebuildIndexes)
    )
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    sys.exit(run_tests() if args.test else main(args))
