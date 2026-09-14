"""Behavior tests for scripts/ai-cat.py."""

from __future__ import annotations

import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as element_tree
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).parents[1] / "ai-cat.py"
MODULE_SPEC = importlib.util.spec_from_file_location("ai_cat", SCRIPT)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
AI_CAT = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = AI_CAT
MODULE_SPEC.loader.exec_module(AI_CAT)


class AiCatTest(unittest.TestCase):
    """Test the command through its CLI boundary."""

    def run_command(
        self,
        directory: Path,
        *arguments: str,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """Run ai-cat in directory and return its completed process."""
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=directory,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def parse_output(
        self, result: subprocess.CompletedProcess[str]
    ) -> element_tree.Element:
        """Assert success and parse XML stdout."""
        self.assertEqual(result.returncode, 0, result.stderr)
        return element_tree.fromstring(result.stdout)

    def initialize_git(self, directory: Path) -> None:
        """Create the smallest Git repository needed by collection tests."""
        result = subprocess.run(
            ["git", "init", "--quiet"],
            cwd=directory,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_no_arguments_prints_help_without_collecting_files(self) -> None:
        """No input exits successfully with the command help."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            result = self.run_command(Path(temporary_directory))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage:", result.stdout)
        self.assertIn("--git-diff", result.stdout)
        self.assertNotIn("<ai-cat", result.stdout)

    def test_text_empty_binary_and_non_utf8_files(self) -> None:
        """The command classifies files and emits only valid text content."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            (directory / "text.txt").write_text(
                "hello & <world>", encoding="utf-8"
            )
            (directory / "empty.txt").touch()
            (directory / "binary.bin").write_bytes(b"\x00\x01")
            (directory / "non-utf8.txt").write_bytes(b"\xff")
            (directory / "invalid-data.txt").write_bytes(b"valid\x01utf-8")

            root = self.parse_output(
                self.run_command(
                    directory,
                    "text.txt",
                    "empty.txt",
                    "binary.bin",
                    "non-utf8.txt",
                    "invalid-data.txt",
                )
            )

            entries = {
                entry.attrib["path"]: entry for entry in root.findall("file")
            }
            self.assertEqual(entries["text.txt"].attrib["status"], "text")
            self.assertEqual(entries["text.txt"].text, "hello & <world>")
            self.assertEqual(entries["empty.txt"].attrib["status"], "empty")
            self.assertIsNone(entries["empty.txt"].text)
            self.assertEqual(entries["binary.bin"].attrib["status"], "binary")
            self.assertEqual(entries["non-utf8.txt"].attrib["status"], "binary")
            self.assertEqual(
                entries["invalid-data.txt"].attrib["status"], "invalid-data"
            )
            self.assertIsNone(entries["invalid-data.txt"].text)

    def test_recursive_collection_omits_ignored_but_explicit_file_is_included(
        self,
    ) -> None:
        """Directory inputs honor ignore rules while explicit files override them."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            self.initialize_git(directory)
            (directory / ".gitignore").write_text(
                "ignored.txt\n", encoding="utf-8"
            )
            (directory / "kept.txt").write_text("kept", encoding="utf-8")
            (directory / "ignored.txt").write_text("ignored", encoding="utf-8")

            recursive_root = self.parse_output(self.run_command(directory, "."))
            recursive_paths = {
                entry.attrib["path"] for entry in recursive_root.findall("file")
            }
            self.assertIn("kept.txt", recursive_paths)
            self.assertNotIn("ignored.txt", recursive_paths)
            self.assertFalse(
                any(path.startswith(".git/") for path in recursive_paths)
            )

            explicit_root = self.parse_output(
                self.run_command(directory, "ignored.txt")
            )
            self.assertEqual(
                [
                    entry.attrib["path"]
                    for entry in explicit_root.findall("file")
                ],
                ["ignored.txt"],
            )

    def test_special_text_remains_valid_xml(self) -> None:
        """Escaping preserves XML-significant text and CDATA terminator text."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            content = "<tag>&value]]>tail"
            (directory / "special.txt").write_text(content, encoding="utf-8")

            root = self.parse_output(self.run_command(directory, "special.txt"))

            entry = root.find("file")
            self.assertIsNotNone(entry)
            assert entry is not None
            self.assertEqual(entry.text, content)

    def test_recursive_collection_skips_symlinks(self) -> None:
        """Recursive collection never emits a symlink target."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            self.initialize_git(directory)
            (directory / "actual.txt").write_text("actual", encoding="utf-8")
            try:
                (directory / "linked.txt").symlink_to(directory / "actual.txt")
            except OSError as error:
                self.skipTest(f"symlinks are unavailable: {error}")

            root = self.parse_output(self.run_command(directory, "."))
            paths = {entry.attrib["path"] for entry in root.findall("file")}
            self.assertIn("actual.txt", paths)
            self.assertNotIn("linked.txt", paths)

    def test_git_diff_uses_current_directory_and_marks_source(self) -> None:
        """Git diff output is a text entry with the gitdiff source taxonomy."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            self.initialize_git(directory)
            (directory / "changed.txt").write_text("before\n", encoding="utf-8")
            result = subprocess.run(
                ["git", "add", "changed.txt"],
                cwd=directory,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            (directory / "changed.txt").write_text("after\n", encoding="utf-8")

            root = self.parse_output(self.run_command(directory, "--git-diff"))

            entry = next(
                item
                for item in root.findall("file")
                if item.attrib.get("source") == "gitdiff"
            )
            self.assertEqual(entry.attrib["status"], "text")
            self.assertIsNotNone(entry.text)
            assert entry.text is not None
            self.assertIn("diff --git", entry.text)

    def test_git_diff_uses_specified_directory(self) -> None:
        """An optional --git-diff path selects that working directory."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            root_directory = Path(temporary_directory)
            repository = root_directory / "repository"
            repository.mkdir()
            self.initialize_git(repository)
            changed = repository / "changed.txt"
            changed.write_text("before\n", encoding="utf-8")
            result = subprocess.run(
                ["git", "add", "changed.txt"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            changed.write_text("after\n", encoding="utf-8")

            root = self.parse_output(
                self.run_command(root_directory, "--git-diff", str(repository))
            )

            entry = root.find("file")
            self.assertIsNotNone(entry)
            assert entry is not None
            self.assertEqual(entry.attrib["source"], "gitdiff")
            self.assertEqual(entry.attrib["path"], "repository")
            self.assertEqual(entry.attrib["status"], "text")

    def test_unavailable_git_and_invalid_path_raise_input_errors(self) -> None:
        """Focused unit tests cover command failures without a Git installation."""
        with mock.patch.object(
            AI_CAT.subprocess, "run", side_effect=FileNotFoundError
        ):
            with self.assertRaisesRegex(AI_CAT.InputError, "git is required"):
                AI_CAT.is_git_ignored(Path("input.txt"), Path.cwd())
            with self.assertRaisesRegex(AI_CAT.InputError, "git is required"):
                AI_CAT.git_diff_entry(Path.cwd(), False)
        with self.assertRaisesRegex(AI_CAT.InputError, "not a regular file"):
            list(AI_CAT.selected_files([Path("missing-input")], Path.cwd()))

    def test_write_document_combines_file_and_diff_entries(self) -> None:
        """Focused unit test covers rendering multiple input source types."""
        output = io.StringIO()
        entries = (
            AI_CAT.Entry("text.txt", "text", "text]]>tail"),
            AI_CAT.Entry("repository", "unread", source="gitdiff"),
        )
        with mock.patch("sys.stdout", output):
            AI_CAT.write_document(entries, dry_run=True)

        root = element_tree.fromstring(output.getvalue())
        self.assertEqual(root.attrib["dry-run"], "true")
        text_entry, diff_entry = root.findall("file")
        self.assertEqual(text_entry.text, "text]]>tail")
        self.assertEqual(diff_entry.attrib["source"], "gitdiff")
        self.assertEqual(diff_entry.attrib["status"], "unread")

    def test_dry_run_omits_content_and_does_not_run_git_diff(self) -> None:
        """Dry-run emits a manifest without content or a Git executable."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            (directory / "text.txt").write_text(
                "secret content", encoding="utf-8"
            )
            (directory / "empty.txt").touch()
            (directory / "binary.bin").write_bytes(b"\x00")
            environment = dict(os.environ, PATH="")

            root = self.parse_output(
                self.run_command(
                    directory,
                    "text.txt",
                    "empty.txt",
                    "binary.bin",
                    "--git-diff",
                    "--dry-run",
                    environment=environment,
                )
            )

            self.assertEqual(root.attrib["dry-run"], "true")
            entries = {
                entry.attrib["path"]: entry for entry in root.findall("file")
            }
            self.assertEqual(entries["text.txt"].attrib["status"], "text")
            self.assertIsNone(entries["text.txt"].text)
            self.assertEqual(entries["empty.txt"].attrib["status"], "empty")
            self.assertEqual(entries["binary.bin"].attrib["status"], "binary")
            self.assertEqual(entries["."].attrib["status"], "unread")
            self.assertEqual(entries["."].attrib["source"], "gitdiff")
            self.assertNotIn(
                "secret content",
                self.run_command(directory, "text.txt", "--dry-run").stdout,
            )


if __name__ == "__main__":
    unittest.main()
