from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path
from typing import Any

import yaml

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESULTS = {"success", "partial", "failure", "blocked"}


class StateError(ValueError):
    pass


def _strings(value: Any, label: str, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(x, str) and x.strip() for x in value
    ):
        raise StateError(f"{label} must be a list of non-empty strings")
    if nonempty and not value:
        raise StateError(f"{label} must not be empty")
    return value


def validate_task(
    value: Any, label: str = "step", completed: bool = False
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise StateError(f"{label} must be a mapping")
    if not isinstance(value.get("slug"), str) or not SLUG.fullmatch(value["slug"]):
        raise StateError(f"{label}.slug must be lowercase kebab-case")
    if not isinstance(value.get("intent"), str) or not value["intent"].strip():
        raise StateError(f"{label}.intent is required")
    _strings(value.get("criteria"), f"{label}.criteria", True)
    if completed:
        do, validation = value.get("do"), value.get("validate")
        if (
            not isinstance(do, dict)
            or not isinstance(do.get("summary"), str)
            or not do["summary"].strip()
        ):
            raise StateError(f"{label}.do.summary is required")
        _strings(do.get("evidence"), f"{label}.do.evidence")
        if not isinstance(validation, dict) or validation.get("result") not in RESULTS:
            raise StateError(f"{label}.validate.result is invalid")
        _strings(validation.get("evidence"), f"{label}.validate.evidence")
    return value


def is_completed(step: dict[str, Any]) -> bool:
    return "do" in step or "validate" in step


def validate_state(state: Any) -> dict[str, Any]:
    if not isinstance(state, dict):
        raise StateError("STEP file must be a mapping")
    if state.get("version") != 1:
        raise StateError("version must be 1")
    if not isinstance(state.get("goal"), str) or not state["goal"].strip():
        raise StateError("goal is required")
    _strings(state.get("lessons"), "lessons")
    history = state.get("history")
    if not isinstance(history, list):
        raise StateError("history must be a list")
    historical_slugs: set[str] = set()
    for i, step in enumerate(history):
        slug = validate_task(step, f"history[{i}]", True)["slug"]
        if slug in historical_slugs:
            raise StateError(f"history contains duplicate slug: {slug}")
        historical_slugs.add(slug)
    current = state.get("current")
    if current is not None:
        validate_task(current, "current", is_completed(current))
        if current["slug"] in historical_slugs:
            raise StateError("current slug already exists in history")
    next_steps = state.get("next")
    if not isinstance(next_steps, list):
        raise StateError("next must be a list")
    next_slugs = [
        validate_task(step, f"next[{i}]")["slug"] for i, step in enumerate(next_steps)
    ]
    if len(next_slugs) != len(set(next_slugs)):
        raise StateError("next contains duplicate slug")
    if any(slug in historical_slugs for slug in next_slugs):
        raise StateError("next slug already exists in history")
    recommended = state.get("recommended")
    if recommended is not None and recommended not in next_slugs:
        raise StateError("recommended must name a next step or be null")
    if not isinstance(state.get("completed"), bool):
        raise StateError("completed must be boolean")
    if state["completed"]:
        if current is not None or next_steps or recommended is not None:
            raise StateError("terminal state cannot have current, next, or recommended")
    elif current is None and not next_steps:
        raise StateError("non-terminal state requires current or next")
    elif current is None and recommended is None:
        raise StateError("state without current requires a recommendation")
    elif (
        current is not None
        and is_completed(current)
        and not next_steps
        and recommended is not None
    ):
        raise StateError("final-signoff state requires null recommendation")
    return state


def create_state(goal: str, lessons: list[str] | None = None) -> dict[str, Any]:
    return {
        "version": 1,
        "goal": goal,
        "lessons": lessons or [],
        "history": [],
        "current": None,
        "next": [],
        "recommended": None,
        "completed": False,
    }


def load_state(path: Path) -> dict[str, Any]:
    try:
        return validate_state(yaml.safe_load(path.read_text()))
    except OSError as exc:
        raise StateError(f"cannot read STEP file: {exc}") from exc
    except yaml.YAMLError as exc:
        raise StateError(f"invalid STEP YAML: {exc}") from exc


def write_atomic(path: Path, state: dict[str, Any]) -> None:
    validate_state(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as stream:
        yaml.safe_dump(state, stream, sort_keys=False, allow_unicode=True)
        temp = Path(stream.name)
    try:
        os.replace(temp, path)
    except OSError:
        temp.unlink(missing_ok=True)
        raise
