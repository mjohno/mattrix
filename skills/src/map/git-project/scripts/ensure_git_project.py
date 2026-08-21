#!/usr/bin/env python3
"""Create or safely synchronize one workspace Git branch clone.

Usage:
    WORK_ROOT=/workspace python ensure_git_project.py --project team/app \
        [--branch master] [--from master] [--checkout app-master]
    WORK_ROOT=/workspace python ensure_git_project.py --project team/app \
        --remote URL --branch feature-name [--from master]
    python ensure_git_project.py --test

Remote mode clones `--from` and creates a new local `--branch` without
pushing it. Stdout is one JSON result. Diagnostics are written to stderr.
Exit status is zero for a completed operation and one for invalid or blocked
state.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Sequence
from contextlib import redirect_stdout
from dataclasses import dataclass
from io import StringIO
from pathlib import Path, PurePosixPath, PureWindowsPath
from unittest import mock

log = logging.getLogger(__name__)


class BlockedError(Exception):
    """A condition that this conservative command must not repair."""


class GitLaunchError(BlockedError):
    """Git could not start in the current environment."""

    def __init__(self, error: OSError) -> None:
        self.error = error
        super().__init__(
            "Git is required but could not start. Install Git from "
            f"https://git-scm.com/downloads and ensure `git` is on PATH: {error}"
        )


@dataclass(frozen=True)
class Request:
    root: Path
    project: PurePosixPath
    branch: str
    source: str
    checkout_name: str
    source_remote: str | None

    @property
    def remote(self) -> Path:
        return self.root / "remotes" / self.project.with_suffix(".git")

    @property
    def project_directory(self) -> Path:
        return self.root / "projects" / self.project

    @property
    def checkout(self) -> Path:
        return self.project_directory / self.checkout_name


def configure_logging(level: str) -> None:
    """Send diagnostics to stderr."""
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
        force=True,
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command inputs."""
    parser = argparse.ArgumentParser(
        description=(
            "Create or synchronize a local Git branch clone, or clone a "
            "remote and create a new local branch."
        )
    )
    parser.add_argument("--project", help="relative project path")
    parser.add_argument("--branch", default="master", help="target branch")
    parser.add_argument(
        "--from", dest="source", default="master", help="source branch"
    )
    parser.add_argument("--checkout", help="direct child clone directory")
    parser.add_argument(
        "--remote",
        dest="source_remote",
        help="remote URL to clone before creating the local branch",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report planned changes without changing the workspace",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    parser.add_argument("--test", action="store_true", help="run inline tests")
    return parser.parse_args(argv)


def git(
    directory: Path | None, *arguments: str
) -> subprocess.CompletedProcess[str]:
    """Run Git without raising for its exit status."""
    command = ["git"]
    if directory is not None:
        command.extend(["-C", str(directory)])
    command.extend(arguments)
    try:
        return subprocess.run(
            command, text=True, capture_output=True, check=False
        )
    except OSError as error:
        raise GitLaunchError(error) from error


def git_output(directory: Path | None, *arguments: str) -> str | None:
    """Return Git stdout when successful, otherwise None."""
    result = git(directory, *arguments)
    if result.returncode != 0:
        log.debug(
            "git %s failed: %s", " ".join(arguments), result.stderr.strip()
        )
        return None
    return result.stdout.strip()


def require_git(directory: Path | None, *arguments: str) -> str:
    """Run Git or stop with its useful diagnostic."""
    result = git(directory, *arguments)
    if result.returncode != 0:
        detail = (
            result.stderr or result.stdout
        ).strip() or "Git command failed"
        raise BlockedError(f"git {' '.join(arguments)}: {detail}")
    return result.stdout.strip()


def valid_project(value: str) -> PurePosixPath:
    """Validate a relative organizational project path."""
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or "\\" in value
        or any(part in ("", ".", "..") for part in path.parts)
    ):
        raise BlockedError("project must be a non-empty relative path")
    return path


def valid_branch(value: str, label: str) -> str:
    """Validate a Git branch name without changing repository state."""
    if not value or git(None, "check-ref-format", "--branch", value).returncode:
        raise BlockedError(f"{label} is not a valid branch name: {value!r}")
    return value


def checkout_name(branch: str, value: str | None) -> str:
    """Return one direct-child checkout directory name."""
    name = (value if value is not None else branch).replace("/", "-")
    if (
        not name
        or name in (".", "..")
        or "/" in name
        or "\\" in name
        or Path(name).name != name
    ):
        raise BlockedError("checkout must name one project child directory")
    return name


def request_from(args: argparse.Namespace) -> Request:
    """Build a validated request from CLI inputs and WORK_ROOT."""
    root_value = os.environ.get("WORK_ROOT")
    if not root_value:
        raise BlockedError("WORK_ROOT is required")
    root = Path(root_value).expanduser().resolve()
    if not root.is_dir():
        raise BlockedError("WORK_ROOT must name an existing directory")
    if not args.project:
        raise BlockedError("--project is required")
    branch = valid_branch(args.branch, "branch")
    source = valid_branch(args.source, "from")
    if args.source_remote is not None:
        if not args.source_remote.strip() or args.source_remote.startswith("-"):
            raise BlockedError("remote must be a non-empty URL or path")
        if args.checkout is not None:
            raise BlockedError("--checkout cannot be used with --remote")
        if branch == source:
            raise BlockedError(
                "--branch must differ from --from in remote mode"
            )
    return Request(
        root,
        valid_project(args.project),
        branch,
        source,
        checkout_name(branch, args.checkout),
        args.source_remote,
    )


def is_bare(path: Path) -> bool:
    """Return whether path is a valid bare repository."""
    return git_output(path, "rev-parse", "--is-bare-repository") == "true"


def is_worktree(path: Path) -> bool:
    """Return whether path is a valid non-bare Git working tree."""
    return (
        git_output(path, "rev-parse", "--is-inside-work-tree") == "true"
        and git_output(path, "rev-parse", "--is-bare-repository") == "false"
    )


def relative_remote_url(checkout: Path, remote: Path) -> str:
    """Return the canonical remote URL relative to a checkout."""
    return os.path.relpath(remote, checkout)


def has_ref(repository: Path, branch: str) -> bool:
    """Return whether a branch reference exists."""
    return (
        git(
            repository,
            "show-ref",
            "--verify",
            "--quiet",
            f"refs/heads/{branch}",
        ).returncode
        == 0
    )


def remote_is_empty(remote: Path) -> bool:
    """Return whether a bare remote has no references."""
    return not bool(git_output(remote, "for-each-ref", "--format=%(refname)"))


def local_url_is_canonical(checkout: Path, remote: Path) -> bool:
    """Return whether local resolves to the project's canonical bare remote."""
    url = git_output(checkout, "remote", "get-url", "local")
    if not url or Path(url).is_absolute() or PureWindowsPath(url).is_absolute():
        return False
    return (checkout / url).resolve() == remote.resolve()


def branch_is_tracked(checkout: Path, branch: str) -> bool:
    """Return whether the checked-out branch tracks local/branch."""
    current = git_output(checkout, "symbolic-ref", "--quiet", "--short", "HEAD")
    upstream = git_output(checkout, "rev-parse", "--abbrev-ref", "@{upstream}")
    return current == branch and upstream == f"local/{branch}"


def worktree_is_clean(checkout: Path) -> bool:
    """Return whether a checkout has no staged, unstaged, or untracked work."""
    return git_output(checkout, "status", "--porcelain") == ""


def identity() -> dict[str, str]:
    """Read Git identity for agent display without requiring a repository."""
    return {
        "username": git_output(None, "config", "--get", "user.name") or "unset",
        "email": git_output(None, "config", "--get", "user.email") or "unset",
    }


def inspect_remote_clone(request: Request) -> None:
    """Validate a remote-clone request before creating any paths."""
    assert request.source_remote is not None
    project = request.project_directory
    checkout = request.checkout
    projects = request.root / "projects"
    if projects.exists() and (not projects.is_dir() or projects.is_symlink()):
        raise BlockedError(f"workspace path is not a directory: {projects}")
    if project.exists() and (not project.is_dir() or project.is_symlink()):
        raise BlockedError(f"project is not a directory: {project}")
    if checkout.exists():
        raise BlockedError(f"checkout already exists: {checkout}")
    if (
        git(
            None,
            "ls-remote",
            "--exit-code",
            "--heads",
            request.source_remote,
            f"refs/heads/{request.source}",
        ).returncode
        != 0
    ):
        raise BlockedError(
            f"source branch does not exist in remote: {request.source}"
        )


def inspect_existing(request: Request) -> bool:
    """Validate existing state and return whether the remote is empty."""
    for root in (request.root / "remotes", request.root / "projects"):
        if root.exists() and (not root.is_dir() or root.is_symlink()):
            raise BlockedError(f"workspace path is not a directory: {root}")

    remote = request.remote
    project = request.project_directory
    checkout = request.checkout
    if remote.exists() and (
        not remote.is_dir() or remote.is_symlink() or not is_bare(remote)
    ):
        raise BlockedError(f"remote is not a valid bare repository: {remote}")
    if project.exists() and (not project.is_dir() or project.is_symlink()):
        raise BlockedError(f"project is not a directory: {project}")
    if checkout.exists():
        if checkout.is_symlink() or not is_worktree(checkout):
            raise BlockedError(
                f"checkout is not a valid working tree: {checkout}"
            )
        if not local_url_is_canonical(checkout, remote):
            raise BlockedError(
                f"checkout local remote is not canonical: {checkout}"
            )
        if git(checkout, "ls-remote", "local").returncode != 0:
            raise BlockedError(
                f"checkout local remote is unreachable: {checkout}"
            )
        if not worktree_is_clean(checkout):
            raise BlockedError(f"checkout has local changes: {checkout}")

    if not remote.exists():
        if request.branch != "master":
            raise BlockedError(
                "a new empty remote can create only the unborn master branch"
            )
        return True

    empty = remote_is_empty(remote)
    if empty:
        if request.branch != "master":
            raise BlockedError(
                "an empty remote can create only the unborn master branch"
            )
        return True

    target_exists = has_ref(remote, request.branch)
    if not target_exists and not has_ref(remote, request.source):
        raise BlockedError(
            f"source branch does not exist in canonical remote: {request.source}"
        )
    if checkout.exists() and not branch_is_tracked(checkout, request.branch):
        raise BlockedError(
            f"checkout does not track local/{request.branch}: {checkout}"
        )
    return False


def ensure_directories(request: Request) -> None:
    """Create only missing workspace and project directories."""
    (request.root / "remotes").mkdir(parents=True, exist_ok=True)
    (request.root / "projects").mkdir(parents=True, exist_ok=True)
    request.remote.parent.mkdir(parents=True, exist_ok=True)
    request.project_directory.mkdir(parents=True, exist_ok=True)


def create_remote_if_missing(request: Request) -> bool:
    """Create the bare remote with master as its default symbolic branch."""
    if request.remote.exists():
        return False
    require_git(
        None, "init", "--bare", "--initial-branch=master", str(request.remote)
    )
    return True


def create_target_branch_if_missing(request: Request) -> bool:
    """Create the requested target from its existing source branch."""
    if has_ref(request.remote, request.branch):
        return False
    require_git(request.remote, "branch", request.branch, request.source)
    return True


def clone_if_missing(request: Request, unborn: bool) -> bool:
    """Clone the requested branch from local when no checkout exists."""
    if request.checkout.exists():
        return False
    clone_url = os.path.relpath(request.remote, request.project_directory)
    local_url = relative_remote_url(request.checkout, request.remote)
    arguments = ["clone", "--origin", "local"]
    if not unborn:
        arguments.extend(["--branch", request.branch])
    arguments.extend([clone_url, str(request.checkout)])
    require_git(request.project_directory, *arguments)
    require_git(request.checkout, "remote", "set-url", "local", local_url)
    require_git(request.checkout, "ls-remote", "local")
    return True


def clone_remote_branch(request: Request) -> None:
    """Clone the source branch and create the requested local branch."""
    assert request.source_remote is not None
    (request.root / "projects").mkdir(parents=True, exist_ok=True)
    request.project_directory.mkdir(parents=True, exist_ok=True)
    require_git(
        request.project_directory,
        "clone",
        "--origin",
        "origin",
        "--branch",
        request.source,
        request.source_remote,
        str(request.checkout),
    )
    require_git(
        request.checkout,
        "switch",
        "--create",
        request.branch,
        f"origin/{request.source}",
    )


def synchronize(request: Request, unborn: bool) -> str:
    """Fetch and fast-forward an existing branch, or report unborn state."""
    if unborn:
        return "unborn"
    require_git(request.checkout, "fetch", "local")
    if not branch_is_tracked(request.checkout, request.branch):
        raise BlockedError(
            f"checkout does not track local/{request.branch}: {request.checkout}"
        )
    if (
        git(
            request.checkout,
            "merge-base",
            "--is-ancestor",
            "HEAD",
            f"local/{request.branch}",
        ).returncode
        != 0
    ):
        raise BlockedError(f"fast-forward is not possible: {request.checkout}")
    require_git(
        request.checkout, "merge", "--ff-only", f"local/{request.branch}"
    )
    return "synchronized"


def planned_actions(request: Request, unborn: bool) -> list[str]:
    """Describe mutations that a non-dry operation would make."""
    actions: list[str] = []
    for directory in (request.root / "remotes", request.root / "projects"):
        if not directory.exists():
            actions.append(f"create directory: {directory}")
    if not request.remote.exists():
        actions.append(f"create bare remote: {request.remote}")
    if not request.project_directory.exists():
        actions.append(f"create project directory: {request.project_directory}")
    if unborn:
        if not request.checkout.exists():
            actions.append(f"clone unborn master branch: {request.checkout}")
        actions.append("report unborn branch")
        return actions
    if not has_ref(request.remote, request.branch):
        actions.append(
            f"create branch {request.branch} from {request.source}: {request.remote}"
        )
    if not request.checkout.exists():
        actions.append(f"clone branch {request.branch}: {request.checkout}")
    else:
        actions.append(f"fetch and fast-forward: {request.checkout}")
    return actions


def execute(request: Request, dry_run: bool = False) -> dict[str, object]:
    """Perform the validated operation and return machine-readable data."""
    if request.source_remote is not None:
        inspect_remote_clone(request)
        actions = [
            f"clone branch {request.source} from {request.source_remote}: "
            f"{request.checkout}",
            f"create local branch {request.branch}: {request.checkout}",
        ]
        if dry_run:
            return {
                "status": "planned",
                "dry_run": True,
                "actions": actions,
                "branch": request.branch,
                "checkout_name": request.checkout_name,
                "checkout": str(request.checkout),
                "remote": request.source_remote,
                "identity": identity(),
            }
        clone_remote_branch(request)
        return {
            "status": "cloned",
            "project": request.project.as_posix(),
            "branch": request.branch,
            "checkout_name": request.checkout_name,
            "checkout": str(request.checkout),
            "remote": request.source_remote,
            "identity": identity(),
        }

    unborn = inspect_existing(request)
    if dry_run:
        return {
            "status": "planned",
            "dry_run": True,
            "actions": planned_actions(request, unborn),
            "branch": request.branch,
            "checkout_name": request.checkout_name,
            "checkout": str(request.checkout),
            "remote": str(request.remote),
            "identity": identity(),
        }
    ensure_directories(request)
    remote_created = create_remote_if_missing(request)
    branch_created = False
    if not unborn:
        branch_created = create_target_branch_if_missing(request)
    clone_created = clone_if_missing(request, unborn)
    status = synchronize(request, unborn)
    return {
        "status": status,
        "project": request.project.as_posix(),
        "branch": request.branch,
        "checkout_name": request.checkout_name,
        "checkout": str(request.checkout),
        "remote": str(request.remote),
        "remote_created": remote_created,
        "branch_created": branch_created,
        "clone_created": clone_created,
        "identity": identity(),
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command and print exactly one JSON result."""
    args = parse_args(argv)
    configure_logging(args.log_level)
    if args.test:
        return run_tests()
    result: dict[str, object]
    try:
        result = execute(request_from(args), args.dry_run)
    except GitLaunchError as error:
        log.error("%s", error)
        result = {
            "status": "blocked",
            "reason": str(error),
            "exception": {
                "type": type(error.error).__name__,
                "message": str(error.error),
            },
            "identity": {"username": "unavailable", "email": "unavailable"},
        }
        print(json.dumps(result, sort_keys=True))
        return 1
    except BlockedError as error:
        log.error("%s", error)
        result = {
            "status": "blocked",
            "reason": str(error),
            "identity": identity(),
        }
        print(json.dumps(result, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


def run_command(root: Path, *arguments: str) -> tuple[int, dict[str, object]]:
    """Run main in a test workspace and decode its stdout result."""
    previous = os.environ.get("WORK_ROOT")
    os.environ["WORK_ROOT"] = str(root)
    try:
        output = StringIO()
        with redirect_stdout(output):
            code = main(list(arguments))
        return code, json.loads(output.getvalue())
    finally:
        if previous is None:
            os.environ.pop("WORK_ROOT", None)
        else:
            os.environ["WORK_ROOT"] = previous


def seed_master(root: Path, project: str) -> Path:
    """Create one committed master branch in a test canonical remote."""
    remote = root / "remotes" / f"{project}.git"
    remote.parent.mkdir(parents=True)
    require_git(None, "init", "--bare", "--initial-branch=master", str(remote))
    seed = root / "seed"
    require_git(None, "init", "--initial-branch=master", str(seed))
    require_git(seed, "config", "user.name", "Test User")
    require_git(seed, "config", "user.email", "test@example.invalid")
    (seed / "README").write_text("seed\n", encoding="utf-8")
    require_git(seed, "add", "README")
    require_git(seed, "commit", "-m", "seed")
    require_git(seed, "remote", "add", "local", str(remote))
    require_git(seed, "push", "local", "master")
    return seed


class GitProjectTests(unittest.TestCase):
    def test_git_launch_failure_returns_exception(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch(
                f"{__name__}.subprocess.run",
                side_effect=FileNotFoundError("git"),
            ):
                code, result = run_command(
                    Path(temporary), "--project", "team/app"
                )
            self.assertEqual(code, 1)
            self.assertEqual(result["status"], "blocked")
            exception = result["exception"]
            identity_data = result["identity"]
            assert isinstance(exception, dict)
            assert isinstance(identity_data, dict)
            self.assertEqual(exception["type"], "FileNotFoundError")
            self.assertEqual(identity_data["username"], "unavailable")

    def test_project_validation_rejects_unsafe_paths(self) -> None:
        for project in ("", "/app", "../app", "team/../app", "team\\app"):
            with self.subTest(project=project):
                with self.assertRaises(BlockedError):
                    valid_project(project)

    def test_checkout_name_normalizes_branch_slashes(self) -> None:
        self.assertEqual(checkout_name("feature/login", None), "feature-login")
        with self.assertRaises(BlockedError):
            checkout_name("master", "team\\app")

    def test_dry_run_does_not_create_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code, result = run_command(
                root, "--project", "team/app", "--dry-run"
            )
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "planned")
            self.assertTrue(result["dry_run"])
            self.assertFalse((root / "remotes").exists())
            self.assertFalse((root / "projects").exists())

    def test_empty_remote_creates_unborn_clone(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code, result = run_command(root, "--project", "team/app")
            checkout = root / "projects/team/app/master"
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "unborn")
            self.assertTrue(is_bare(root / "remotes/team/app.git"))
            self.assertTrue(is_worktree(checkout))
            self.assertTrue(
                local_url_is_canonical(checkout, root / "remotes/team/app.git")
            )

    def test_creates_branch_and_clone_from_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            seed_master(root, "team/app")
            code, result = run_command(
                root,
                "--project",
                "team/app",
                "--branch",
                "foo",
                "--checkout",
                "bar",
            )
            checkout = root / "projects/team/app/bar"
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "synchronized")
            self.assertTrue(has_ref(root / "remotes/team/app.git", "foo"))
            self.assertTrue(branch_is_tracked(checkout, "foo"))

    def test_remote_clone_creates_normalized_unpushed_branch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            remote_root = Path(temporary) / "remote"
            seed_master(remote_root, "team/app")
            remote = remote_root / "remotes/team/app.git"
            code, result = run_command(
                root,
                "--project",
                "team/app",
                "--remote",
                str(remote),
                "--branch",
                "feature/idea",
            )
            checkout = root / "projects/team/app/feature-idea"
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "cloned")
            self.assertEqual(result["checkout_name"], "feature-idea")
            self.assertEqual(
                git_output(checkout, "branch", "--show-current"), "feature/idea"
            )
            self.assertFalse(has_ref(remote, "feature/idea"))

    def test_remote_dry_run_does_not_create_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            remote_root = root / "remote"
            seed_master(remote_root, "team/app")
            remote = remote_root / "remotes/team/app.git"
            code, result = run_command(
                root,
                "--project",
                "team/app",
                "--remote",
                str(remote),
                "--branch",
                "feature/idea",
                "--dry-run",
            )
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "planned")
            self.assertEqual(result["checkout_name"], "feature-idea")
            self.assertFalse((root / "projects/team/app/feature-idea").exists())

    def test_test_option_does_not_require_project(self) -> None:
        self.assertIsNone(parse_args(["--test"]).project)

    def test_remote_clone_rejects_empty_remote(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code, result = run_command(
                root,
                "--project",
                "team/app",
                "--remote",
                "",
                "--branch",
                "foo",
            )
            self.assertEqual(code, 1)
            self.assertEqual(result["status"], "blocked")
            self.assertIn("non-empty", str(result["reason"]))

    def test_remote_clone_rejects_checkout_override(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code, result = run_command(
                root,
                "--project",
                "team/app",
                "--remote",
                "https://example.invalid/team/app.git",
                "--branch",
                "foo",
                "--checkout",
                "bar",
            )
            self.assertEqual(code, 1)
            self.assertEqual(result["status"], "blocked")
            self.assertIn("--checkout", str(result["reason"]))

    def test_fast_forwards_existing_clone(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            seed = seed_master(root, "team/app")
            self.assertEqual(run_command(root, "--project", "team/app")[0], 0)
            (seed / "README").write_text("next\n", encoding="utf-8")
            require_git(seed, "commit", "-am", "next")
            require_git(seed, "push", "local", "master")
            code, result = run_command(root, "--project", "team/app")
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "synchronized")

    def test_invalid_remote_stops_before_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            remote = root / "remotes/team/app.git"
            remote.mkdir(parents=True)
            code, result = run_command(root, "--project", "team/app")
            self.assertEqual(code, 1)
            self.assertEqual(result["status"], "blocked")
            self.assertFalse((root / "projects/team/app/master").exists())

    def test_divergent_clone_stops(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            seed = seed_master(root, "team/app")
            self.assertEqual(run_command(root, "--project", "team/app")[0], 0)
            checkout = root / "projects/team/app/master"
            require_git(checkout, "config", "user.name", "Test User")
            require_git(
                checkout, "config", "user.email", "test@example.invalid"
            )
            (checkout / "LOCAL").write_text("local\n", encoding="utf-8")
            require_git(checkout, "add", "LOCAL")
            require_git(checkout, "commit", "-m", "local")
            (seed / "REMOTE").write_text("remote\n", encoding="utf-8")
            require_git(seed, "add", "REMOTE")
            require_git(seed, "commit", "-m", "remote")
            require_git(seed, "push", "local", "master")
            code, result = run_command(root, "--project", "team/app")
            self.assertEqual(code, 1)
            self.assertEqual(result["status"], "blocked")
            self.assertIn("fast-forward", str(result["reason"]))


def run_tests() -> int:
    """Run inline verification for required success and failure paths."""
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GitProjectTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
