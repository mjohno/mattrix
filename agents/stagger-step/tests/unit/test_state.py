from __future__ import annotations

import pytest
from stagger_step.state import StateError, create_state, validate_state

TASK = {"slug": "task", "intent": "Task", "criteria": ["done"]}
DONE = {
    **TASK,
    "do": {"summary": "done", "evidence": []},
    "validate": {"result": "success", "summary": "Ran tests", "evidence": []},
}


def test_state_rejects_recommendation_not_in_next():
    state = {
        "version": 1,
        "goal": "Goal",
        "change_path": None,
        "commit_mode": False,
        "lessons": [],
        "history": [],
        "current": None,
        "next": [TASK],
        "recommended": "other",
        "completed": False,
    }
    with pytest.raises(StateError):
        validate_state(state)


def test_state_accepts_final_signoff_and_rejects_ambiguous_terminal():
    signoff = {
        "version": 1,
        "goal": "Goal",
        "change_path": None,
        "commit_mode": False,
        "lessons": [],
        "history": [],
        "current": DONE,
        "next": [],
        "recommended": "terminate",
        "completed": False,
    }
    assert validate_state(signoff) == signoff
    signoff["completed"] = True
    with pytest.raises(StateError):
        validate_state(signoff)


def test_state_rejects_null_terminal_recommendation():
    state = {
        "version": 1,
        "goal": "Goal",
        "change_path": None,
        "commit_mode": False,
        "lessons": [],
        "history": [],
        "current": DONE,
        "next": [],
        "recommended": None,
        "completed": False,
    }

    with pytest.raises(
        StateError,
        match="final-signoff state requires terminate recommendation",
    ):
        validate_state(state)


def test_fresh_state_has_root_change_and_commit_fields():
    state = create_state("Goal", change_path="artifacts", commit_mode=True)

    assert state["change_path"] == "artifacts"
    assert state["commit_mode"] is True


@pytest.mark.parametrize(
    "field, value", (("change_path", ""), ("commit_mode", "enabled"))
)
def test_state_rejects_invalid_change_configuration(field, value):
    state = create_state("Goal")
    state[field] = value

    with pytest.raises(StateError):
        validate_state(state)
