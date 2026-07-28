#!/usr/bin/env python3
"""Build the local Mattrix Docker image.

Usage:
    python make.py docker-build [--quiet]

Exit status:
    0 on success; otherwise Docker's exit status (127 if Docker is unavailable).
"""

import argparse
import logging
import subprocess
import sys

log = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Mattrix build commands")
    parser.add_argument(
        "command",
        choices=["docker-build"],
        help="Command to run",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress successful-build output; print errors only",
    )
    return parser.parse_args(argv)


def docker_build(quiet: bool) -> int:
    """Build the Mattrix image as mattrix:latest."""
    command = ["docker", "build", "--file", "docker/Dockerfile", "--tag", "mattrix:latest", "."]

    try:
        if quiet:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode:
                sys.stderr.write(result.stdout)
                sys.stderr.write(result.stderr)
            return result.returncode

        return subprocess.run(command).returncode
    except FileNotFoundError:
        log.error("Docker is not installed or is not available on PATH.")
        return 127


def main(argv: list[str] | None = None) -> int:
    """Run the selected build command."""
    args = parse_args(argv)

    if args.command == "docker-build":
        return docker_build(args.quiet)

    return 2


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.ERROR,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )
    sys.exit(main())
