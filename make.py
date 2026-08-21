#!/usr/bin/env python3
"""Run local Mattrix build and Python quality commands.

Usage:
    python make.py <command> [--quiet]

Quality commands target ``agents/``, root Python scripts, and Python files in
``skills/**/scripts/``. Tool configuration lives in root ``pyproject.toml``.
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

log = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parent
BUILD_ROOT = ROOT / "build"
STAGGER_STEP_ROOT = ROOT / "agents" / "stagger-step"
STAGGER_STEP_BUILD = BUILD_ROOT / "stagger-step"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Mattrix build and quality commands"
    )
    parser.add_argument(
        "command",
        choices=[
            "build-stagger-step",
            "clean",
            "docker-build",
            "quality-install",
            "format",
            "format-check",
            "ruff",
            "basedpyright",
            "quality",
        ],
        help="Command to run",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress successful-command output; print errors only",
    )
    return parser.parse_args(argv)


def quality_targets() -> list[str]:
    """Return the monorepo Python areas governed by shared quality checks."""
    skill_scripts = sorted(
        str(path.relative_to(ROOT))
        for path in (ROOT / "skills").glob("**/scripts/*.py")
    )
    return ["agents", "make.py", *skill_scripts]


def run_command(command: list[str], quiet: bool) -> int:
    """Run a command, suppressing successful output when requested."""
    if not quiet:
        return subprocess.run(command, cwd=ROOT, check=False).returncode

    result = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, check=False
    )
    if result.returncode:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
    return result.returncode


def quality_command(command: str) -> list[str]:
    """Build the command line for one configured quality tool."""
    targets = quality_targets()
    tool_commands = {
        "format": [sys.executable, "-m", "ruff", "format", *targets],
        "format-check": [
            sys.executable,
            "-m",
            "ruff",
            "format",
            "--check",
            *targets,
        ],
        "ruff": [sys.executable, "-m", "ruff", "check", *targets],
        "basedpyright": [sys.executable, "-m", "basedpyright", *targets],
    }
    return tool_commands[command]


def build_stagger_step(quiet: bool) -> int:
    """Build the Stagger Step wheel under the shared build directory."""
    STAGGER_STEP_BUILD.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".stagger-step-", dir=STAGGER_STEP_BUILD
    ) as temp:
        source = Path(temp) / "source"
        shutil.copytree(
            STAGGER_STEP_ROOT,
            source,
            ignore=shutil.ignore_patterns(
                "build", "*.egg-info", "__pycache__", ".pytest_cache"
            ),
        )
        command = [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            ".",
            "--no-deps",
            "--wheel-dir",
            str(STAGGER_STEP_BUILD),
        ]
        if not quiet:
            return subprocess.run(command, cwd=source, check=False).returncode
        result = subprocess.run(
            command, cwd=source, capture_output=True, text=True, check=False
        )
        if result.returncode:
            sys.stderr.write(result.stdout)
            sys.stderr.write(result.stderr)
        return result.returncode


def clean(quiet: bool) -> int:
    """Remove generated build, package, cache, and coverage artifacts."""
    directory_names = {
        "build",
        "dist",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        "htmlcov",
        "tmp",
    }
    excluded_names = {".git", ".venv", "env", "venv"}
    artifacts: list[Path] = []

    for parent, directories, files in os.walk(ROOT, topdown=True):
        directories[:] = [
            name for name in directories if name not in excluded_names
        ]
        parent_path = Path(parent)
        artifacts.extend(
            parent_path / name
            for name in directories
            if name in directory_names or name.endswith(".egg-info")
        )
        artifacts.extend(
            parent_path / name
            for name in files
            if name == ".coverage" or name.startswith(".coverage.")
        )

    for artifact in sorted(
        artifacts, key=lambda path: len(path.parts), reverse=True
    ):
        if artifact.is_symlink() or artifact.is_file():
            artifact.unlink(missing_ok=True)
        else:
            shutil.rmtree(artifact, ignore_errors=True)
        if not quiet:
            print(f"Removed {artifact.relative_to(ROOT)}")
    return 0


def docker_build(quiet: bool) -> int:
    """Build the Mattrix image as mattrix:latest."""
    command = [
        "docker",
        "build",
        "--file",
        "docker/Dockerfile",
        "--tag",
        "mattrix:latest",
        ".",
    ]

    try:
        return run_command(command, quiet)
    except FileNotFoundError:
        log.error("Docker is not installed or is not available on PATH.")
        return 127


def main(argv: list[str] | None = None) -> int:
    """Run the selected build command."""
    args = parse_args(argv)

    if args.command == "build-stagger-step":
        return build_stagger_step(args.quiet)

    if args.command == "clean":
        return clean(args.quiet)

    if args.command == "docker-build":
        return docker_build(args.quiet)

    if args.command == "quality-install":
        return run_command(
            [sys.executable, "-m", "pip", "install", "-e", ".[quality]"],
            args.quiet,
        )

    if args.command == "quality":
        for command in ("format-check", "ruff", "basedpyright"):
            result = run_command(quality_command(command), args.quiet)
            if result:
                return result
        return 0

    return run_command(quality_command(args.command), args.quiet)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.ERROR,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )
    sys.exit(main())
