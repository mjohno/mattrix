#!/usr/bin/env python3
"""Validate the Git layout rooted at the required WORK_ROOT environment variable.

Usage:
    WORK_ROOT=/path/to/workspace python scripts/validate_workspace.py

The validator is read-only. It writes its success summary to stdout and any
validation failures or diagnostics to stderr.
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import subprocess
import sys
import unittest
from collections.abc import Sequence
from pathlib import Path, PureWindowsPath

log = logging.getLogger(__name__)

GIT_URL_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def configure_logging(log_level: str) -> None:
    """Configure diagnostics to stderr."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
        force=True,
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse configuration-only command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate the workspace declared by WORK_ROOT.",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="diagnostic log level (default: WARNING)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="run inline unit tests",
    )
    return parser.parse_args(argv)


def run_git(directory: Path, *arguments: str) -> tuple[bool, str]:
    """Run Git in *directory*, returning success and combined diagnostic text."""
    completed = subprocess.run(
        ["git", "-C", str(directory), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )
    output = (completed.stdout + completed.stderr).strip()
    return completed.returncode == 0, output


def git_value(directory: Path, *arguments: str) -> str | None:
    """Return Git stdout for a successful command, otherwise ``None``."""
    success, output = run_git(directory, *arguments)
    if not success:
        log.debug(
            "git -C %s %s failed: %s", directory, " ".join(arguments), output
        )
        return None
    return output.splitlines()[0] if output else ""


def is_bare_repository(directory: Path) -> bool:
    """Return whether *directory* is a valid bare Git repository."""
    return git_value(directory, "rev-parse", "--is-bare-repository") == "true"


def is_worktree(directory: Path) -> bool:
    """Return whether *directory* is a valid non-bare Git working tree."""
    return (
        git_value(directory, "rev-parse", "--is-inside-work-tree") == "true"
        and git_value(directory, "rev-parse", "--is-bare-repository") == "false"
    )


def is_relative_git_path(url: str) -> bool:
    """Return whether a Git remote URL is a relative filesystem path."""
    return bool(url) and not (
        Path(url).is_absolute()
        or PureWindowsPath(url).is_absolute()
        or url.startswith("\\\\")
        or GIT_URL_SCHEME.match(url)
        or ":" in url
    )


def canonical_local_target(checkout: Path, remote_url: str) -> Path:
    """Resolve a relative Git remote path from its checkout directory."""
    return (checkout / remote_url).resolve()


def project_path_for_remote(
    remote: Path, remotes_root: Path, projects_root: Path
) -> Path:
    """Map ``remotes/.../project.git`` to ``projects/.../project``."""
    relative_remote = remote.relative_to(remotes_root)
    return projects_root / relative_remote.with_suffix("")


def find_remotes(remotes_root: Path) -> list[Path]:
    """Return all directories ending in ``.git`` beneath the remotes tree."""
    return sorted(
        (path for path in remotes_root.rglob("*.git") if path.is_dir()),
        key=str,
    )


def child_directories(directory: Path) -> list[Path]:
    """Return immediate child directories, excluding symlinks."""
    return sorted(
        (
            path
            for path in directory.iterdir()
            if path.is_dir() and not path.is_symlink()
        ),
        key=str,
    )


def validate_workspace(root: Path) -> list[str]:
    """Return all deterministic conformance failures for *root*."""
    failures: list[str] = []
    remotes_root = root / "remotes"
    projects_root = root / "projects"

    for required_path in (remotes_root, projects_root):
        if not required_path.is_dir():
            failures.append(f"missing required directory: {required_path}")
    if failures:
        return failures

    remotes = find_remotes(remotes_root)
    expected_projects: set[Path] = set()

    for remote in remotes:
        if not is_bare_repository(remote):
            failures.append(
                f"remote is not a valid bare Git repository: {remote}"
            )

        project = project_path_for_remote(remote, remotes_root, projects_root)
        expected_projects.add(project)
        if not project.is_dir():
            failures.append(
                f"remote has no matching project directory: {remote} -> {project}"
            )

    discovered_projects: set[Path] = set()
    for candidate in projects_root.rglob("*"):
        if not candidate.is_dir() or candidate.is_symlink():
            continue
        if is_worktree(candidate):
            project = candidate.parent
            discovered_projects.add(project)
            if project not in expected_projects:
                failures.append(
                    "checkout has no matching canonical remote/project pair: "
                    f"{candidate} (project: {project})"
                )

    for project in sorted(expected_projects, key=str):
        if not project.is_dir():
            continue
        checkouts = child_directories(project)
        if not checkouts:
            failures.append(f"project has no checkout directories: {project}")
            continue

        for checkout in checkouts:
            if not is_worktree(checkout):
                failures.append(
                    f"checkout is not a valid non-bare Git working tree: {checkout}"
                )
                continue

            local_url = git_value(checkout, "remote", "get-url", "local")
            if local_url is None:
                failures.append(f"checkout has no local remote: {checkout}")
                continue
            if not is_relative_git_path(local_url):
                failures.append(
                    "checkout local remote is not a relative path: "
                    f"{checkout}: {local_url}"
                )
                continue

            expected_remote = remotes_root / project.relative_to(projects_root)
            expected_remote = expected_remote.with_name(
                f"{expected_remote.name}.git"
            )
            actual_remote = canonical_local_target(checkout, local_url)
            if actual_remote != expected_remote.resolve():
                failures.append(
                    "checkout local remote does not match canonical bare remote: "
                    f"{checkout}: expected {expected_remote}, got {actual_remote}"
                )
                continue

            reachable, diagnostic = run_git(checkout, "ls-remote", "local")
            if not reachable:
                detail = f" ({diagnostic})" if diagnostic else ""
                failures.append(
                    f"checkout local remote is unreachable: {checkout}{detail}"
                )

    return failures


def workspace_root() -> Path | None:
    """Read and validate the required WORK_ROOT environment variable."""
    value = os.environ.get("WORK_ROOT")
    if not value:
        return None
    root = Path(value).expanduser().resolve()
    return root if root.is_dir() else None


def main(_args: argparse.Namespace) -> int:
    """Validate WORK_ROOT and return a stable process exit code."""
    root = workspace_root()
    if root is None:
        print(
            "FAIL: WORK_ROOT must name an existing workspace directory.",
            file=sys.stderr,
        )
        return 1

    failures = validate_workspace(root)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1

    print(f"PASS: workspace is valid: {root}")
    return 0


def run_tests() -> int:
    """Run lightweight unit tests for path interpretation helpers."""

    class ValidatorTests(unittest.TestCase):
        def test_relative_git_paths(self) -> None:
            self.assertTrue(
                is_relative_git_path("../../../remotes/team/app.git")
            )
            self.assertTrue(is_relative_git_path("remotes/team/app.git"))
            self.assertFalse(
                is_relative_git_path("/workspace/remotes/team/app.git")
            )
            self.assertFalse(
                is_relative_git_path("file:///workspace/remotes/team/app.git")
            )
            self.assertFalse(
                is_relative_git_path("git@example.test:team/app.git")
            )

        def test_remote_to_project_mapping(self) -> None:
            remotes = Path("/workspace/remotes")
            projects = Path("/workspace/projects")
            remote = remotes / "team" / "app.git"
            self.assertEqual(
                project_path_for_remote(remote, remotes, projects),
                projects / "team" / "app",
            )

        def test_local_target_is_checkout_relative(self) -> None:
            checkout = Path("/workspace/projects/team/app/main")
            self.assertEqual(
                canonical_local_target(
                    checkout, "../../../../remotes/team/app.git"
                ),
                Path("/workspace/remotes/team/app.git"),
            )

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ValidatorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    parsed_args = parse_args(sys.argv[1:])
    configure_logging(parsed_args.log_level)
    if parsed_args.test:
        sys.exit(run_tests())
    sys.exit(main(parsed_args))
