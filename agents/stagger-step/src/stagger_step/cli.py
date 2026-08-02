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
from .git import CommitMode
from .harness import PiRpcHarness
from .loop import StepLoop, TransitionError
from .normalizer import ROLES, normalize_packet
from .state import StateError, create_state, load_state, write_atomic

logger = logging.getLogger("stagger_step.cli")


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
        "--commit",
        action="store_true",
        help="create a local Git commit after each approved completed packet",
    )
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
        "normalize", help="normalize one role YAML response from standard input"
    )
    normalize.add_argument("--role", choices=ROLES, required=True)
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
        raise StateError("commit mode requires a clean baseline for the current packet")
    sha = commit.commit(current, current["commit_base"])
    history_packet = changed["history"][-1]
    history_packet.pop("commit_base", None)
    if sha is not None:
        history_packet["commit"] = sha
    # DECISION: a crash after commit and before write_atomic may lose this SHA.
    # Restart intentionally continues from persisted STEP state without reconciliation.
    return changed


def _afk_failure(prepared: dict[str, Any], outcomes: list[str]) -> bool:
    current = prepared.get("current")
    validation = current.get("validate") if isinstance(current, dict) else None
    result = validation.get("result") if isinstance(validation, dict) else None
    if not isinstance(result, str):
        return False
    outcomes.append(result)
    del outcomes[:-10]
    return result in {"failure", "blocked"}


def run_session(
    path: Path,
    state: dict[str, Any],
    loop: StepLoop,
    commit: CommitMode | None = None,
) -> int:
    """Continuously apply the one-shot gate's prepare, revise, and approve flow."""
    afk = False
    outcomes: list[str] = []
    while True:
        state = load_state(path)
        try:
            prepared = prepare(state, loop, commit)
        except KeyboardInterrupt:
            if not afk:
                raise
            afk = False
            logger.info("AFK disabled by Ctrl+C; returning to manual mode")
            continue
        if prepared != state:
            write_atomic(path, prepared)
        emit(loop.gate(prepared))
        if afk and _afk_failure(prepared, outcomes):
            afk = False
            logger.info("AFK disabled by failure threshold; returning to manual mode")
        if afk:
            logger.info("AFK automatically approved the current gate")
            user_input = "approved"
        else:
            print("STEP response: ", end="", file=sys.stderr, flush=True)
            try:
                user_input = input()
            except EOFError:
                return 0
        if user_input == "break":
            emit({"changed": False})
            return 0
        if user_input == "afk":
            afk = True
            outcomes.clear()
            logger.info("AFK enabled")
            user_input = "approved"
        changed = (
            approve(prepared, loop, commit)
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
    raw_path = args.file or os.getenv("STEP_FILE")
    diagnostic_path = Path(raw_path) if raw_path else None
    interrupted = False

    def on_sigint(signum: int, frame: Any) -> None:
        nonlocal interrupted
        del signum, frame
        logger.debug("SIGINT received; cancelling active STEP harness process")
        if interrupted:
            os._exit(130)
        interrupted = True
        write_diagnostics(diagnostic_path, event="SIGINT")
        raise KeyboardInterrupt

    previous_sigint = signal.signal(signal.SIGINT, on_sigint)
    try:
        if args.command == "normalize":
            try:
                candidate = yaml.safe_load(sys.stdin.read())
            except yaml.YAMLError as exc:
                raise StateError(f"invalid role YAML: {exc}") from exc
            emit(normalize_packet(args.role, candidate))
            return 0
        if args.command == "init":
            path = path_from(args, create=True)
            if path.exists():
                raise StateError("refusing to replace an existing STEP file")
            commit = CommitMode(path, Path.cwd()) if args.commit else None
            if commit is not None:
                commit.begin()
            loop = StepLoop(
                PiRpcHarness(
                    session_enabled=args.harness_session == "on",
                    session_scope=str(path.resolve()),
                )
            )
            state = loop.bootstrap(create_state(args.goal, args.lesson))
            write_atomic(path, state)
            if args.session:
                return run_session(path, state, loop, commit)
            emit({"ok": True, "created": str(path), "gate": loop.gate(state)})
            return 0
        path = path_from(args)
        state = load_state(path)
        if args.command == "validate":
            emit({"ok": True, "state": state})
            return 0
        commit = CommitMode(path, Path.cwd()) if args.commit else None
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
            )
        )
        if args.command == "gate":
            if args.response == "break":
                emit({"changed": False})
                return 0
            prepared = prepare(state, loop, commit)
            if prepared != state:
                write_atomic(path, prepared)
            if args.response is None:
                emit(loop.gate(prepared))
                return 0
            if args.response == "approved":
                changed = approve(prepared, loop, commit)
                if not changed["completed"]:
                    changed = prepare(changed, loop, commit)
            else:
                changed = loop.revise(prepared, args.response)
            write_atomic(path, changed)
            emit({"ok": True, "changed": True, "gate": loop.gate(changed)})
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
            "STEP harness error: %s", exc, exc_info=logger.isEnabledFor(logging.DEBUG)
        )
        return 3
    finally:
        signal.signal(signal.SIGINT, previous_sigint)


if __name__ == "__main__":
    raise SystemExit(main())
