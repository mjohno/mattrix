from __future__ import annotations

import pytest
from stagger_step.state import (
    StateError,
    create_state,
    default_role_settings,
    default_token_usage,
    validate_state,
)

TASK = {"slug": "task", "intent": "Task", "criteria": ["done"]}
DONE = {
    **TASK,
    "work": {"summary": "done", "evidence": []},
    "validate": {"result": "success", "summary": "Ran tests", "evidence": []},
}


def test_state_accepts_unstarted_and_rejects_ambiguous_empty_state():
    state = create_state("Goal")
    assert validate_state(state) == state

    state["recommended"] = "terminate"
    with pytest.raises(
        StateError, match="unstarted state requires no recommendation"
    ):
        validate_state(state)


def test_state_rejects_recommendation_not_in_next():
    state = {
        "version": 1,
        "goal": "Goal",
        "role_settings": default_role_settings(),
        "token_usage": default_token_usage(),
        "change_path": None,
        "commit_mode": False,
        "packet_history": 5,
        "lessons": [],
        "history": [],
        "current": None,
        "next": [TASK],
        "recommended": "other",
        "completed": False,
    }
    with pytest.raises(StateError):
        validate_state(state)


def test_state_rejects_retired_do_packet():
    state = {
        "version": 1,
        "goal": "Goal",
        "role_settings": default_role_settings(),
        "token_usage": default_token_usage(),
        "change_path": None,
        "commit_mode": False,
        "packet_history": 5,
        "lessons": [],
        "history": [],
        "current": {
            **TASK,
            "do": {"summary": "retired", "evidence": []},
            "validate": DONE["validate"],
        },
        "next": [],
        "recommended": "terminate",
        "completed": False,
    }

    with pytest.raises(
        StateError, match="current.do is retired; use current.work"
    ):
        validate_state(state)


def test_state_accepts_final_signoff_and_rejects_ambiguous_terminal():
    signoff = {
        "version": 1,
        "goal": "Goal",
        "role_settings": default_role_settings(),
        "token_usage": default_token_usage(),
        "change_path": None,
        "commit_mode": False,
        "packet_history": 5,
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
        "role_settings": default_role_settings(),
        "token_usage": default_token_usage(),
        "change_path": None,
        "commit_mode": False,
        "packet_history": 5,
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


def test_state_requires_complete_valid_role_settings():
    state = create_state("Goal")
    del state["role_settings"]["worker"]

    with pytest.raises(
        StateError, match="role_settings must contain each STEP role"
    ):
        validate_state(state)

    state = create_state("Goal")
    state["role_settings"]["worker"]["thinking"] = "unsupported"

    with pytest.raises(
        StateError, match="role_settings.worker.thinking is invalid"
    ):
        validate_state(state)


def test_fresh_state_has_root_change_commit_and_packet_history_fields():
    state = create_state("Goal", change_path="artifacts", commit_mode=True)

    assert state["change_path"] == "artifacts"
    assert state["commit_mode"] is True
    assert state["packet_history"] == 3
    assert state["role_settings"] == default_role_settings()
    assert state["token_usage"] == {
        "input": 0,
        "output": 0,
        "cache_read": 0,
        "cache_write": 0,
        "total": 0,
        "cost": 0.0,
    }


def test_state_rejects_missing_token_usage():
    state = create_state("Goal")
    del state["token_usage"]

    with pytest.raises(StateError, match="token_usage"):
        validate_state(state)


def test_state_rejects_inconsistent_token_usage_total():
    state = create_state("Goal")
    state["token_usage"]["input"] = 1

    with pytest.raises(StateError, match="token_usage.total"):
        validate_state(state)


@pytest.mark.parametrize(
    "field, value",
    (("change_path", ""), ("commit_mode", "enabled"), ("packet_history", 0)),
)
def test_state_rejects_invalid_change_configuration(field, value):
    state = create_state("Goal")
    state[field] = value

    with pytest.raises(StateError):
        validate_state(state)
