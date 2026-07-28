from __future__ import annotations

import argparse
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any

import yaml

from .diagnostics import write_diagnostics
from .harness import PiRpcHarness
from .loop import StepLoop, TransitionError
from .state import StateError, create_state, load_state, write_atomic


def path_from(args: argparse.Namespace, create: bool = False) -> Path:
    raw = args.file or os.getenv("STEP_FILE")
    if not raw:
        raise StateError("set STEP_FILE or pass --file")
    path = Path(raw)
    if not create and not path.exists():
        raise StateError(f"STEP file does not exist: {path}")
    return path


def emit(value: Any) -> None:
    print(yaml.safe_dump(value, sort_keys=False), end="")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Deterministic, approval-gated STEP loop")
    p.add_argument("--file", help="STEP file path; defaults to STEP_FILE")
    p.add_argument(
        "--log-level",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        default=os.getenv("STAGGER_STEP_LOG_LEVEL", "ERROR").upper(),
        help="stderr logging level (default: ERROR)",
    )
    p.add_argument(
        "--harness-session",
        choices=("on", "off"),
        default=os.getenv("STAGGER_STEP_HARNESS_SESSION", "off").lower(),
        help="persist and reuse role-specific Pi sessions (default: off)",
    )
    sub = p.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="create a new STEP state")
    init.add_argument("--goal", required=True)
    init.add_argument("--lesson", action="append", default=[])
    init.add_argument(
        "--session",
        action="store_true",
        help="enter the continuous session after initialization",
    )
    sub.add_parser("validate", help="validate existing manual YAML state")
    gate = sub.add_parser("gate", help="apply one STEP gate response and exit")
    gate.add_argument(
        "response", nargs="?", help="exact approved, break, or revision feedback"
    )
    sub.add_parser(
        "session", help="render a gate and accept one human response in this process"
    )
    return p


def run_session(path: Path, state: dict[str, Any], loop: StepLoop) -> int:
    """Continuously apply the one-shot gate's prepare, revise, and approve flow."""
    while True:
        state = load_state(path)
        prepared = loop.prepare(state)
        if prepared != state:
            write_atomic(path, prepared)
        emit(loop.gate(prepared))
        print("STEP response: ", end="", file=sys.stderr, flush=True)
        try:
            user_input = input()
        except EOFError:
            return 0
        if user_input == "break":
            emit({"changed": False})
            return 0
        changed = (
            loop.approve(prepared)
            if user_input == "approved"
            else loop.revise(prepared, user_input)
        )
        write_atomic(path, changed)
        emit({"ok": True, "changed": True})
        if changed["completed"]:
            return 0
        state = changed


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s %(name)s: %(message)s",
    )
    logger = logging.getLogger("stagger_step.cli")
    raw_path = args.file or os.getenv("STEP_FILE")
    diagnostic_path = Path(raw_path) if raw_path else None
    interrupted = False

    def on_sigint(signum: int, frame: Any) -> None:
        nonlocal interrupted
        del signum, frame
        if interrupted:
            os._exit(130)
        interrupted = True
        write_diagnostics(diagnostic_path, event="SIGINT")
        raise KeyboardInterrupt

    previous_sigint = signal.signal(signal.SIGINT, on_sigint)
    try:
        if args.command == "init":
            path = path_from(args, create=True)
            if path.exists():
                raise StateError("refusing to replace an existing STEP file")
            loop = StepLoop(
                PiRpcHarness(
                    session_enabled=args.harness_session == "on",
                    session_scope=str(path.resolve()),
                )
            )
            state = loop.bootstrap(create_state(args.goal, args.lesson))
            write_atomic(path, state)
            if args.session:
                return run_session(path, state, loop)
            emit({"ok": True, "created": str(path), "gate": loop.gate(state)})
            return 0
        path = path_from(args)
        state = load_state(path)
        if args.command == "validate":
            emit({"ok": True, "state": state})
            return 0
        loop = StepLoop(
            PiRpcHarness(
                session_enabled=args.harness_session == "on",
                session_scope=str(path.resolve()),
            )
        )
        if args.command == "gate":
            if args.response == "break":
                emit({"changed": False})
                return 0
            prepared = loop.prepare(state)
            if prepared != state:
                write_atomic(path, prepared)
            if args.response is None:
                emit(loop.gate(prepared))
                return 0
            if args.response == "approved":
                changed = loop.approve(prepared)
                if not changed["completed"]:
                    changed = loop.prepare(changed)
            else:
                changed = loop.revise(prepared, args.response)
            write_atomic(path, changed)
            emit({"ok": True, "changed": True, "gate": loop.gate(changed)})
            return 0
        return run_session(path, state, loop)
    except (StateError, TransitionError) as exc:
        logger.error("STEP error: %s", exc)
        return 2
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        write_diagnostics(diagnostic_path, event="unhandled_failure", error=exc)
        logger.critical(
            "STEP harness error: %s", exc, exc_info=logger.isEnabledFor(logging.DEBUG)
        )
        return 3
    finally:
        signal.signal(signal.SIGINT, previous_sigint)


if __name__ == "__main__":
    raise SystemExit(main())
