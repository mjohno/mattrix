#!/usr/bin/env python3
"""Render selected project content as one XML document for AI chat uploads."""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import quoteattr

log = logging.getLogger("ai_cat")
XML_TEXT_RANGES = ((0x20, 0xD7FF), (0xE000, 0xFFFD), (0x10000, 0x10FFFF))

# NOTE(assumption): Treat non-UTF-8 content as binary.


@dataclass(frozen=True)
class Entry:
    """One file-like XML entry."""

    path: str
    status: str
    content: str | None = None
    source: str | None = None


class InputError(Exception):
    """An invalid CLI input or unavailable Git operation."""


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Render selected files and directories as one XML document. "
            "Directories omit Git-ignored files and never follow symlinks."
        )
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="file or directory to export",
    )
    parser.add_argument(
        "--git-diff",
        nargs="?",
        const=Path("."),
        type=Path,
        metavar="PATH",
        help="add git diff from PATH, or the current directory when PATH is omitted",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="emit only the entry manifest; do not emit content or run git diff",
    )
    args = parser.parse_args(argv)
    args.help_text = parser.format_help()
    args.show_help = not args.paths and args.git_diff is None
    return args


def display_path(path: Path, working_directory: Path) -> str:
    """Return a path relative to the current working directory."""
    return os.path.relpath(path, working_directory)


def is_git_ignored(path: Path, working_directory: Path) -> bool:
    """Return whether Git ignore rules match path, including tracked paths."""
    relative_path = display_path(path, working_directory)
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(working_directory),
                "check-ignore",
                "--no-index",
                "--quiet",
                "--",
                relative_path,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise InputError(
            "git is required for recursive directory inputs"
        ) from error
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    detail = result.stderr.strip() or "Git ignore check failed"
    raise InputError(detail)


def recursive_files(directory: Path, working_directory: Path) -> Iterable[Path]:
    """Yield non-ignored regular files without traversing symlinks."""
    for root, directories, files in os.walk(directory, followlinks=False):
        root_path = Path(root)
        directories[:] = sorted(
            name
            for name in directories
            if name != ".git" and not (root_path / name).is_symlink()
        )
        for name in sorted(files):
            path = root_path / name
            if path.is_symlink() or not path.is_file():
                continue
            if not is_git_ignored(path, working_directory):
                yield path


def selected_files(
    paths: Sequence[Path], working_directory: Path
) -> Iterable[Path]:
    """Yield selected files, keeping explicit files even when Git ignores them."""
    seen: set[Path] = set()
    for supplied_path in paths:
        expanded_path = supplied_path.expanduser()
        path = Path(
            os.path.abspath(
                expanded_path
                if expanded_path.is_absolute()
                else working_directory / expanded_path
            )
        )
        if path.is_symlink():
            log.warning("skipping symlink: %s", supplied_path)
            continue
        if path.is_file():
            candidates: Iterable[Path] = (path,)
        elif path.is_dir():
            candidates = recursive_files(path, working_directory)
        else:
            raise InputError(
                f"path is not a regular file or directory: {supplied_path}"
            )
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                yield candidate


def is_xml_text(text: str) -> bool:
    """Return whether text is legal in an XML 1.0 character data section."""
    return all(
        character in "\t\n\r"
        or any(
            lower <= ord(character) <= upper for lower, upper in XML_TEXT_RANGES
        )
        for character in text
    )


def classify_file(path: Path, include_content: bool) -> tuple[str, str | None]:
    """Classify a file and, when requested, return valid XML text content."""
    content = path.read_bytes()
    if not content:
        return "empty", None
    if b"\x00" in content:
        return "binary", None
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return "binary", None
    if not is_xml_text(text):
        return "invalid-data", None
    return "text", text if include_content else None


def file_entries(
    paths: Sequence[Path], working_directory: Path, dry_run: bool
) -> Iterable[Entry]:
    """Create XML entries for selected files."""
    for path in selected_files(paths, working_directory):
        status, content = classify_file(path, not dry_run)
        yield Entry(display_path(path, working_directory), status, content)


def git_diff_entry(directory: Path, dry_run: bool) -> Entry:
    """Create an XML entry for a Git diff, unless dry-run requests a manifest."""
    resolved_directory = directory.expanduser().resolve()
    if not resolved_directory.is_dir():
        raise InputError(f"git diff path is not a directory: {directory}")
    path = display_path(resolved_directory, Path.cwd())
    if dry_run:
        return Entry(path, "unread", source="gitdiff")
    try:
        result = subprocess.run(
            ["git", "-C", str(resolved_directory), "diff"],
            check=False,
            capture_output=True,
        )
    except FileNotFoundError as error:
        raise InputError("git is required for --git-diff") from error
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise InputError(detail or "git diff failed")
    if not result.stdout:
        return Entry(path, "empty", source="gitdiff")
    try:
        content = result.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return Entry(path, "binary", source="gitdiff")
    if not is_xml_text(content):
        return Entry(path, "invalid-data", source="gitdiff")
    return Entry(path, "text", content, source="gitdiff")


def cdata(text: str) -> str:
    """Return text in CDATA sections without an illegal terminator sequence."""
    return f"<![CDATA[{text.replace(']]>', ']]]]><![CDATA[>')}]]>"


def write_entry(entry: Entry) -> None:
    """Write one XML element to standard output."""
    attributes = [
        f"path={quoteattr(entry.path)}",
        f"status={quoteattr(entry.status)}",
    ]
    if entry.source is not None:
        attributes.append(f"source={quoteattr(entry.source)}")
    if entry.content is None:
        print(f"  <file {' '.join(attributes)} />")
        return
    print(f"  <file {' '.join(attributes)}>{cdata(entry.content)}</file>")


def write_document(entries: Iterable[Entry], dry_run: bool) -> None:
    """Write the complete XML document to standard output."""
    print('<?xml version="1.0" encoding="UTF-8"?>')
    root_attributes = ' dry-run="true"' if dry_run else ""
    print(f"<ai-cat{root_attributes}>")
    for entry in entries:
        write_entry(entry)
    print("</ai-cat>")


def configure_logging() -> None:
    """Configure diagnostics on standard error."""
    logging.basicConfig(
        level=logging.WARNING, format="%(levelname)s: %(message)s"
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Collect inputs and write their XML representation."""
    args = parse_args(argv)
    if args.show_help:
        print(args.help_text, end="")
        return 0
    working_directory = Path.cwd().resolve()
    try:
        entries = list(
            file_entries(args.paths, working_directory, args.dry_run)
        )
        if args.git_diff is not None:
            entries.append(git_diff_entry(args.git_diff, args.dry_run))
    except (InputError, OSError) as error:
        log.error("%s", error)
        return 2
    write_document(entries, args.dry_run)
    return 0


if __name__ == "__main__":
    configure_logging()
    raise SystemExit(main())
