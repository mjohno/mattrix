from __future__ import annotations

import pytest
from stagger_step.state import StateError, validate_state

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
        "lessons": [],
        "history": [],
        "current": DONE,
        "next": [],
        "recommended": None,
        "completed": False,
    }
    assert validate_state(signoff) == signoff
    signoff["completed"] = True
    with pytest.raises(StateError):
        validate_state(signoff)
