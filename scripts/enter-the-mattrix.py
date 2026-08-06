#!/usr/bin/env python3
"""Enter the Mattrix Docker image with the current directory as its workspace.

Examples:
    enter-the-mattrix.py
    enter-the-mattrix.py --workspace ../project
    enter-the-mattrix.py --image acme/mattrix-project:latest
    enter-the-mattrix.py -- stagger-step session
    enter-the-mattrix.py --dry-run

The launcher reports only safe Git, Pi, and Docker configuration metadata to
stderr. It never prints environment variables, credentials, or file contents.
"""

from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence

log = logging.getLogger("enter_the_mattrix")

IMAGE_DEFAULT = "mattrix:latest"
CONTAINER_WORKSPACE = "/workspace"
CONTAINER_HOME = "/home/mattrix"


def run_text(command: Sequence[str]) -> str | None:
    """Return command stdout, logging a safe diagnostic when it is unavailable."""
    try:
        result = subprocess.run(
            command, text=True, capture_output=True, check=False
        )
    except FileNotFoundError:
        log.warning("%s is not available on PATH", command[0])
        return None
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "command failed"
        log.warning("%s", detail)
        return None
    return result.stdout.strip()


def git_setting(workspace: Path, name: str) -> str:
    """Read one non-secret Git identity setting, or report that it is unset."""
    value = run_text(("git", "-C", str(workspace), "config", "--get", name))
    return value if value else "(unset)"


def log_git_config(workspace: Path, gitconfig: Path) -> None:
    """Log safe Git identity and configuration-location metadata."""
    log.info("Git workspace: %s", workspace)
    log.info("Git user.name: %s", git_setting(workspace, "user.name"))
    log.info("Git user.email: %s", git_setting(workspace, "user.email"))
    log.info(
        "Git config mount: %s",
        gitconfig if gitconfig.is_file() else "(no host .gitconfig)",
    )


def log_pi_config(pi_dir: Path) -> None:
    """Log Pi configuration location and safe file-name metadata only."""
    entries = []
    if pi_dir.is_dir():
        entries = sorted(path.name for path in pi_dir.iterdir())[:20]
    log.info("Pi config directory: %s", pi_dir)
    log.info("Pi config entries: %s", ", ".join(entries) or "(none)")


def log_docker_config(image: str) -> bool:
    """Log Docker runtime metadata and report whether the requested image exists."""
    context = run_text(("docker", "context", "show"))
    version = run_text(
        ("docker", "version", "--format", "client={{.Client.Version}} server={{.Server.Version}}")
    )
    image_id = run_text(("docker", "image", "inspect", "--format", "{{.Id}}", image))
    log.info("Docker context: %s", context or "(unavailable)")
    log.info("Docker version: %s", version or "(unavailable)")
    log.info("Docker image %s: %s", image, image_id or "(missing)")
    return image_id is not None


def mount(source: Path, destination: str, *, readonly: bool = False) -> str:
    """Build a Docker --mount value without platform-specific volume syntax."""
    value = f"type=bind,src={source},dst={destination}"
    return f"{value},readonly" if readonly else value


def docker_command(args: argparse.Namespace) -> list[str]:
    """Build the Docker invocation without exposing forwarded command arguments in logs."""
    command = [
        "docker",
        "run",
        "--rm",
        "-it",
        "--init",
        "--workdir",
        CONTAINER_WORKSPACE,
        "--mount",
        mount(args.workspace, CONTAINER_WORKSPACE),
        "--mount",
        mount(args.pi_dir, f"{CONTAINER_HOME}/.pi"),
    ]
    if args.gitconfig.is_file():
        command.extend(("--mount", mount(args.gitconfig, f"{CONTAINER_HOME}/.gitconfig", readonly=True)))
    command.append(args.image)
    if args.command:
        command.extend(("-lc", 'exec "$@"', "mattrix", *args.command))
    return command


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse launcher arguments and normalize all host paths."""
    parser = argparse.ArgumentParser(
        description="Enter Mattrix in a Docker-mounted project workspace."
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="project workspace to mount (default: current directory)",
    )
    parser.add_argument("--image", default=IMAGE_DEFAULT, help="Docker image to run")
    parser.add_argument(
        "--pi-dir",
        type=Path,
        default=Path.home() / ".pi",
        help="host Pi configuration directory to mount",
    )
    parser.add_argument(
        "--gitconfig",
        type=Path,
        default=Path.home() / ".gitconfig",
        help="host Git configuration file to mount read-only when present",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate inputs and report configuration without starting Docker",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="optional command to run in the image; prefix it with --",
    )
    args = parser.parse_args(argv)
    args.workspace = args.workspace.expanduser().resolve()
    args.pi_dir = args.pi_dir.expanduser().resolve()
    args.gitconfig = args.gitconfig.expanduser().resolve()
    return args


def configure_logging() -> None:
    """Configure human diagnostics on stderr."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    """Validate host configuration, report safe metadata, then enter Docker."""
    args = parse_args(argv)
    if not args.workspace.is_dir():
        log.error("workspace is not a directory: %s", args.workspace)
        return 2
    if not args.pi_dir.is_dir():
        log.error("Pi configuration directory is not a directory: %s", args.pi_dir)
        return 2
    if shutil.which("docker") is None:
        log.error("Docker is not available on PATH")
        return 127

    log_git_config(args.workspace, args.gitconfig)
    log_pi_config(args.pi_dir)
    image_exists = log_docker_config(args.image)
    if not image_exists:
        log.error("build the image first: python make.py docker-build")
        return 2
    if args.dry_run:
        log.info("Dry run complete; Docker was not started")
        return 0

    return subprocess.run(docker_command(args), check=False).returncode


if __name__ == "__main__":
    configure_logging()
    raise SystemExit(main())
