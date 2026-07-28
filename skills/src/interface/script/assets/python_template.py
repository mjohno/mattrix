#!/usr/bin/env python3
"""
<DESCRIPTION: One-line summary of what this script does.>

Examples:
    python <SCRIPT_NAME>.py --dry-run
    python <SCRIPT_NAME>.py --log-level DEBUG
    python <SCRIPT_NAME>.py --test
    python <SCRIPT_NAME>.py --help

Stdout is reserved for intentional data output such as IPC, shell pipelines,
or user-requested CLI results. Diagnostics and logs go to stderr.
"""

import argparse
import logging
import sys

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Core Functionality
# ---------------------------------------------------------------------------

def main(args: argparse.Namespace) -> int:
    """Run the script's primary workflow and return an exit code."""
    log.info("Starting script with arguments: %s", args)

    # <ORCHESTRATE CORE LOGIC HERE>
    # Use print(...) only for intentional stdout data output.

    return 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# def helper(...) -> ...:
#     """Reusable, testable logic belongs in typed helper functions."""
#     ...


# ---------------------------------------------------------------------------
# Boilerplate Setup
# ---------------------------------------------------------------------------

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
        description="<DESCRIPTION>",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes",
    )
    parser.add_argument(
        "--log-level",
        default="CRITICAL",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: CRITICAL)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run inline tests",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Test Harness
# ---------------------------------------------------------------------------

def run_tests() -> int:
    """Run inline tests using unittest. Return 0 if all pass, 1 if any fail."""
    import unittest

    class TestScript(unittest.TestCase):
        def test_parse_args(self) -> None:
            """Test that parse_args behaves as expected."""
            dry_run = parse_args(["--dry-run", "--log-level", "DEBUG"])
            self.assertTrue(dry_run.dry_run)
            self.assertEqual(dry_run.log_level, "DEBUG")

            test_run = parse_args(["--test"])
            self.assertTrue(test_run.test)
            self.assertFalse(test_run.dry_run)
            self.assertEqual(test_run.log_level, "CRITICAL")

            with self.assertRaises(SystemExit):
                parse_args(["--help"])

        # <ADDITIONAL TESTS GO HERE>

    suite = unittest.TestLoader().loadTestsFromTestCase(TestScript)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    configure_logging(args.log_level)

    if args.test:
        sys.exit(run_tests())

    sys.exit(main(args))
