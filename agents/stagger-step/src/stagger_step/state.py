from __future__ import annotations
import os
import re
import tempfile
from pathlib import Path
from typing import Any
import yaml

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESULTS = {"success", "partial", "failure", "blocked"}

class StateError(ValueError): pass

def _strings(value: Any, label: str, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value):
        raise StateError(f"{label} must be a list of non-empty strings")
    if nonempty and not value: raise StateError(f"{label} must not be empty")
    return value

def validate_task(value: Any, label: str = "packet", completed: bool = False) -> dict[str, Any]:
    if not isinstance(value, dict): raise StateError(f"{label} must be a mapping")
    if not isinstance(value.get("slug"), str) or not SLUG.fullmatch(value["slug"]): raise StateError(f"{label}.slug must be lowercase kebab-case")
    if not isinstance(value.get("intent"), str) or not value["intent"].strip(): raise StateError(f"{label}.intent is required")
    _strings(value.get("criteria"), f"{label}.criteria", True)
    if completed:
        do, validation = value.get("do"), value.get("validate")
        if not isinstance(do, dict) or not isinstance(do.get("summary"), str) or not do["summary"].strip(): raise StateError(f"{label}.do.summary is required")
        if not isinstance(do, dict): raise StateError(f"{label}.do must be a mapping")
        _strings(do.get("evidence"), f"{label}.do.evidence")
        if not isinstance(validation, dict) or validation.get("result") not in RESULTS: raise StateError(f"{label}.validate.result is invalid")
        _strings(validation.get("evidence"), f"{label}.validate.evidence")
    return value

def validate_gate(gate: Any) -> dict[str, Any]:
    if not isinstance(gate, dict): raise StateError("gate must be a mapping")
    if not isinstance(gate.get("goal"), str) or not gate["goal"].strip(): raise StateError("gate.goal is required")
    _strings(gate.get("lessons"), "gate.lessons")
    current = gate.get("current_packet")
    if current is not None: validate_task(current, "gate.current_packet", True)
    proposals = gate.get("proposed_next_packets")
    if not isinstance(proposals, list): raise StateError("gate.proposed_next_packets must be a list")
    slugs = [validate_task(packet, f"gate.proposed_next_packets[{i}]")["slug"] for i, packet in enumerate(proposals)]
    if len(slugs) != len(set(slugs)): raise StateError("gate contains duplicate proposed packet slugs")
    rec = gate.get("recommendation")
    if rec is not None and rec not in slugs: raise StateError("gate.recommendation must name a proposed packet or be null")
    return gate

def validate_state(state: Any) -> dict[str, Any]:
    if not isinstance(state, dict): raise StateError("STEP file must be a mapping")
    if state.get("version") != 1: raise StateError("version must be 1")
    if not isinstance(state.get("goal"), str) or not state["goal"].strip(): raise StateError("goal is required")
    _strings(state.get("lessons"), "lessons")
    history = state.get("history")
    if not isinstance(history, list): raise StateError("history must be a list")
    slugs: set[str] = set()
    for i, packet in enumerate(history):
        slug = validate_task(packet, f"history[{i}]", True)["slug"]
        if slug in slugs: raise StateError(f"history contains duplicate slug: {slug}")
        slugs.add(slug)
    active = state.get("active_packet")
    if active is not None:
        slug = validate_task(active, "active_packet")["slug"]
        if slug in slugs: raise StateError("active_packet slug already exists in history")
    if not isinstance(state.get("completed"), bool): raise StateError("completed must be boolean")
    if state["completed"] and active is not None: raise StateError("completed state cannot have active_packet")
    if history and active is None and not state["completed"]: raise StateError("non-terminal state with history requires active_packet")
    return state

def create_state(goal: str, lessons: list[str] | None = None) -> dict[str, Any]:
    state = {"version": 1, "goal": goal, "lessons": lessons or [], "history": [], "active_packet": None, "completed": False}
    return validate_state(state)

def load_state(path: Path) -> dict[str, Any]:
    try: return validate_state(yaml.safe_load(path.read_text()))
    except OSError as exc: raise StateError(f"cannot read STEP file: {exc}") from exc
    except yaml.YAMLError as exc: raise StateError(f"invalid STEP YAML: {exc}") from exc

def write_atomic(path: Path, state: dict[str, Any]) -> None:
    validate_state(state); path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
        yaml.safe_dump(state, stream, sort_keys=False, allow_unicode=True); temp = Path(stream.name)
    try: os.replace(temp, path)
    except OSError:
        temp.unlink(missing_ok=True); raise
