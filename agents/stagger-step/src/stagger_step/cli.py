from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path
from typing import Any
import yaml
from .harness import PiRpcHarness
from .loop import StepLoop, TransitionError
from .state import StateError, create_state, load_state, write_atomic

def path_from(args: argparse.Namespace, create: bool = False) -> Path:
    raw = args.file or os.getenv("STEP_FILE")
    if not raw: raise StateError("set STEP_FILE or pass --file")
    path = Path(raw)
    if not create and not path.exists(): raise StateError(f"STEP file does not exist: {path}")
    return path

def emit(value: Any) -> None: print(yaml.safe_dump(value, sort_keys=False), end="")

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Deterministic, approval-gated STEP loop")
    p.add_argument("--file", help="STEP file path; defaults to STEP_FILE")
    sub = p.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="create a new STEP state")
    init.add_argument("--goal", required=True); init.add_argument("--lesson", action="append", default=[])
    sub.add_parser("validate", help="validate existing manual YAML state")
    gate = sub.add_parser("gate", help="run the applicable role sequence and render a YAML gate")
    gate.add_argument("--revision")
    sub.add_parser("session", help="render a gate and accept one human response in this process")
    return p

def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "init":
            path = path_from(args, create=True)
            if path.exists(): raise StateError("refusing to replace an existing STEP file")
            write_atomic(path, create_state(args.goal, args.lesson)); emit({"ok": True, "created": str(path)}); return 0
        path = path_from(args)
        state = load_state(path)
        if args.command == "validate": emit({"ok": True, "state": state}); return 0
        loop = StepLoop(PiRpcHarness())
        if args.command == "gate": emit(loop.render_gate(state, revision=args.revision)); return 0
        # Pending role output is process-local: it is never serialized to STEP state
        # or accepted back from an arbitrary gate file.
        gate = loop.render_gate(state)
        while True:
            emit(gate)
            user_input = input("STEP response: ")
            if user_input == "approved":
                write_atomic(path, loop.approve(state, gate, user_input)); emit({"ok": True, "changed": True}); return 0
            result = loop.revise(state, gate, user_input)
            if result.get("outcome") == "paused": emit(result); return 0
            gate = result
    except (StateError, TransitionError) as exc:
        print(f"STEP error: {exc}", file=sys.stderr); return 2
    except Exception as exc:
        print(f"STEP harness error: {exc}", file=sys.stderr); return 3
if __name__ == "__main__": raise SystemExit(main())
