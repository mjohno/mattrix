#!/usr/bin/env python3
"""Run local Mattrix build and Python quality commands.

Usage:
    python make.py <command> [--quiet]

Quality commands target ``agents/``, root Python scripts, and Python files in
``skills/**/scripts/``. Tool configuration lives in root ``pyproject.toml``.
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

log = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parent


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Mattrix build and quality commands")
    parser.add_argument(
        "command",
        choices=[
            "docker-build",
            "quality-install",
            "format",
            "format-check",
            "ruff",
            "pylint",
            "mypy",
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
        return subprocess.run(command, cwd=ROOT).returncode

    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
    return result.returncode


def quality_command(command: str) -> list[str]:
    """Build the command line for one configured quality tool."""
    targets = quality_targets()
    tool_commands = {
        "format": [sys.executable, "-m", "black", *targets],
        "format-check": [sys.executable, "-m", "black", "--check", *targets],
        "ruff": [sys.executable, "-m", "ruff", "check", *targets],
        "pylint": [sys.executable, "-m", "pylint", *targets],
        "mypy": [sys.executable, "-m", "mypy", *targets],
    }
    return tool_commands[command]


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

    if args.command == "docker-build":
        return docker_build(args.quiet)

    if args.command == "quality-install":
        return run_command(
            [sys.executable, "-m", "pip", "install", "-e", ".[quality]"], args.quiet
        )

    if args.command == "quality":
        for command in ("format-check", "ruff", "pylint", "mypy"):
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
