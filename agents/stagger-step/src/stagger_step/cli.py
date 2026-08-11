from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import sys
import threading
import time
from pathlib import Path
from typing import Any

from .diagnostics import write_diagnostics
from .git import CommitMode
from .harness import PiRpcHarness
from .loop import StepLoop, TransitionError
from .normalizer import ROLES, normalize_packet
from .render import render_gate
from .state import StateError, create_state, load_state, write_atomic

logger = logging.getLogger("stagger_step.cli")
_INTERRUPT_REQUESTED = threading.Event()


def _request_interrupt() -> None:
    _INTERRUPT_REQUESTED.set()


def _consume_interrupt() -> bool:
    requested = _INTERRUPT_REQUESTED.is_set()
    _INTERRUPT_REQUESTED.clear()
    return requested


def _raise_if_interrupt_requested() -> None:
    if _consume_interrupt():
        raise KeyboardInterrupt


def path_from(args: argparse.Namespace, create: bool = False) -> Path:
    raw = args.file or os.getenv("STEP_FILE")
    if not raw:
        raise StateError("set STEP_FILE or pass --file")
    path = Path(raw)
    if not create and not path.exists():
        raise StateError(f"STEP file does not exist: {path}")
    return path


def emit_gate(gate: dict[str, Any]) -> None:
    print(render_gate(gate), end="")


def emit_response(response: str) -> None:
    """Append the submitted response and a review separator to stdout."""
    print(f"{response}\n\n---")


def is_revision_feedback(value: str) -> bool:
    """Accept meaningful revision feedback, not accidental keystrokes."""
    normalized = value.strip()
    return len(normalized) > 3 and any(char.isalpha() for char in normalized)


def resolve_change_path(step_path: Path, value: str | None) -> str | None:
    """Resolve a configured change path relative to its STEP file."""
    if value is None:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = step_path.parent / path
    path = path.resolve()
    if not path.is_dir():
        raise StateError(f"change_path must name an existing directory: {path}")
    return str(path)


def select_commit_mode(
    state: dict[str, Any], step_path: Path, cwd: Path, commit_off: bool
) -> CommitMode | None:
    """Select persisted commit mode unless this invocation disables it."""
    if not state["commit_mode"] or commit_off:
        return None
    return CommitMode(step_path, cwd)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Deterministic, approval-gated STEP loop"
    )
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
        default=os.getenv("STAGGER_STEP_HARNESS_SESSION", "on").lower(),
        help="persist and reuse role-specific Pi sessions (default: on)",
    )
    sub = p.add_subparsers(dest="command", required=True)
    normalize = sub.add_parser(
        "normalize", help="normalize one role JSON response from standard input"
    )
    normalize.add_argument("--role", choices=ROLES, required=True)
    init = sub.add_parser("init", help="create a new STEP state")
    init.add_argument("--goal", required=True)
    init.add_argument("--lesson", action="append", default=[])
    init.add_argument(
        "--change",
        help="existing artifact directory, resolved relative to the STEP file",
    )
    init.add_argument(
        "--commit",
        action="store_true",
        help="persist local commit mode for this STEP workflow",
    )
    init.add_argument(
        "--session",
        action="store_true",
        help="enter the continuous session after initialization",
    )
    sub.add_parser("validate", help="validate existing manual YAML state")
    gate = sub.add_parser(
        "gate", help="apply one STEP gate response and exit", allow_abbrev=False
    )
    gate.add_argument(
        "response",
        nargs="?",
        help="exact approved, break, or revision feedback with a letter and more than 3 characters",
    )
    gate.add_argument(
        "--commit-off",
        action="store_true",
        help="disable persisted commit mode for this invocation",
    )
    session = sub.add_parser(
        "session",
        help="render a gate and accept one human response in this process",
        allow_abbrev=False,
    )
    session.add_argument(
        "--commit-off",
        action="store_true",
        help="disable persisted commit mode for this session",
    )
    return p


def prepare(
    state: dict[str, Any],
    loop: StepLoop,
    commit: CommitMode | None,
) -> dict[str, Any]:
    base = None
    has_base = False
    active = state.get("current")
    if commit is not None and active is not None and not active.get("do"):
        base = commit.clean_baseline()
        has_base = True
    prepared = loop.prepare(state)
    if has_base and prepared.get("current") is not None:
        prepared["current"]["commit_base"] = base
    return prepared


def approve(
    prepared: dict[str, Any], loop: StepLoop, commit: CommitMode | None
) -> dict[str, Any]:
    changed = loop.approve(prepared)
    current = prepared.get("current")
    if commit is None or current is None:
        return changed
    if "commit_base" not in current:
        raise StateError(
            "commit mode requires a clean baseline for the current packet"
        )
    sha = commit.commit(current, current["commit_base"])
    history_packet = changed["history"][-1]
    history_packet.pop("commit_base", None)
    if sha is not None:
        history_packet["commit"] = sha
    # DECISION: a crash after commit and before write_atomic may lose this SHA.
    # Restart intentionally continues from persisted STEP state without reconciliation.
    return changed


def _afk_stop(prepared: dict[str, Any], outcomes: list[str]) -> str | None:
    current = prepared.get("current")
    validation = current.get("validate") if isinstance(current, dict) else None
    result = validation.get("result") if isinstance(validation, dict) else None
    if not isinstance(result, str):
        return None
    if result == "blocked":
        return "blocked result"
    outcomes.append(result)
    del outcomes[:-10]
    failures = sum(outcome == "failure" for outcome in outcomes)
    if failures > max(1, len(outcomes) / 10):
        return "failure threshold"
    return None


def run_session(
    path: Path,
    state: dict[str, Any],
    loop: StepLoop,
    commit: CommitMode | None = None,
) -> int:
    """Continuously apply the one-shot gate's prepare, revise, and approve flow."""
    afk = False
    outcomes: list[str] = []
    state = load_state(path)
    while True:
        try:
            prepared = prepare(state, loop, commit)
            _raise_if_interrupt_requested()
            _raise_if_interrupt_requested()
            emit_gate(loop.gate(prepared))
            if afk and (stop_reason := _afk_stop(prepared, outcomes)):
                afk = False
                logger.info(
                    "AFK disabled by %s; returning to manual mode", stop_reason
                )
            if afk:
                _raise_if_interrupt_requested()
                logger.info("AFK automatically approved the current gate")
                user_input = "approved"
                displayed_response = "afk"
            else:
                try:
                    user_input = input()
                except EOFError:
                    return 0
                displayed_response = user_input
            emit_response(displayed_response)
            if user_input == "break":
                return 0
            if user_input == "afk":
                afk = True
                outcomes.clear()
                logger.info("AFK enabled")
                user_input = "approved"
            elif user_input != "approved" and not is_revision_feedback(
                user_input
            ):
                logger.info("Ignored nonsensical STEP response")
                continue
            changed = (
                approve(prepared, loop, commit)
                if user_input == "approved"
                else loop.revise(prepared, user_input)
            )
            _raise_if_interrupt_requested()
            if user_input == "approved":
                write_atomic(path, changed)
            _raise_if_interrupt_requested()
            if changed["completed"]:
                return 0
            state = changed
        except KeyboardInterrupt:
            if not afk:
                raise
            _consume_interrupt()
            afk = False
            logger.info("AFK disabled by Ctrl+C; returning to manual mode")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s [%(asctime)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    raw_path = args.file or os.getenv("STEP_FILE")
    diagnostic_path = Path(raw_path) if raw_path else None
    _consume_interrupt()

    def on_sigint(signum: int, frame: Any) -> None:
        del signum, frame
        logger.info(
            "SIGINT received; interrupt requested at the next STEP boundary"
        )
        _request_interrupt()
        write_diagnostics(diagnostic_path, event="SIGINT")
        raise KeyboardInterrupt

    previous_sigint = signal.signal(signal.SIGINT, on_sigint)
    try:
        if args.command == "normalize":
            try:
                candidate = json.load(sys.stdin)
            except json.JSONDecodeError as exc:
                raise StateError(f"invalid role JSON: {exc}") from exc
            print(
                json.dumps(normalize_packet(args.role, candidate)), flush=True
            )
            return 0
        if args.command == "init":
            path = path_from(args, create=True)
            if path.exists():
                raise StateError("refusing to replace an existing STEP file")
            change_path = resolve_change_path(path, args.change)
            commit = CommitMode(path, Path.cwd()) if args.commit else None
            if commit is not None:
                commit.begin()
            loop = StepLoop(
                PiRpcHarness(
                    session_enabled=args.harness_session == "on",
                    session_scope=str(path.resolve()),
                ),
                change_path,
            )
            state = loop.bootstrap(
                create_state(
                    args.goal,
                    args.lesson,
                    change_path=args.change,
                    commit_mode=args.commit,
                )
            )
            write_atomic(path, state)
            if args.session:
                return run_session(path, state, loop, commit)
            emit_gate(loop.gate(state))
            return 0
        path = path_from(args)
        state = load_state(path)
        if args.command == "gate" and args.response == "break":
            return 0
        change_path = resolve_change_path(path, state["change_path"])
        commit = select_commit_mode(state, path, Path.cwd(), args.commit_off)
        if commit is not None:
            pending = state.get("current")
            commit.begin(
                require_clean=not (
                    isinstance(pending, dict)
                    and pending.get("do")
                    and "commit_base" in pending
                )
            )
        loop = StepLoop(
            PiRpcHarness(
                session_enabled=args.harness_session == "on",
                session_scope=str(path.resolve()),
            ),
            change_path,
        )
        if args.command == "validate":
            emit_gate(loop.gate(state))
            return 0
        if args.command == "gate":
            prepared = prepare(state, loop, commit)
            if args.response is None:
                emit_gate(loop.gate(prepared))
                return 0
            if args.response == "approved":
                changed = approve(prepared, loop, commit)
                write_atomic(path, changed)
                displayed = (
                    prepare(changed, loop, commit)
                    if not changed["completed"]
                    else changed
                )
            elif not is_revision_feedback(args.response):
                emit_gate(loop.gate(prepared))
                return 0
            else:
                changed = loop.revise(prepared, args.response)
                displayed = changed
            emit_gate(loop.gate(displayed))
            return 0
        return run_session(path, state, loop, commit)
    except (StateError, TransitionError) as exc:
        logger.error("STEP error: %s", exc)
        return 2
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        write_diagnostics(diagnostic_path, event="unhandled_failure", error=exc)
        logger.critical(
            "STEP harness error: %s",
            exc,
            exc_info=logger.isEnabledFor(logging.DEBUG),
        )
        return 3
    finally:
        signal.signal(signal.SIGINT, previous_sigint)


if __name__ == "__main__":
    raise SystemExit(main())
