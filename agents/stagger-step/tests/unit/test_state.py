from __future__ import annotations

import pytest
from stagger_step.loop import StepLoop
from stagger_step.state import StateError, validate_state

TASK = {"slug": "task", "intent": "Task", "criteria": ["done"]}
DONE = {
    **TASK,
    "do": {"summary": "done", "evidence": []},
    "validate": {"result": "success", "evidence": []},
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


def test_approval_consumes_the_promoted_step_and_clears_recommendation():
    class NoHarness:
        pass

    first, second = {**TASK, "slug": "first"}, {**TASK, "slug": "second"}
    state = {
        "version": 1,
        "goal": "Goal",
        "lessons": [],
        "history": [],
        "current": None,
        "next": [first, second],
        "recommended": "first",
        "completed": False,
    }
    approved = StepLoop(NoHarness()).approve(state)
    assert approved["current"]["slug"] == "first"
    assert [step["slug"] for step in approved["next"]] == ["second"]
    assert approved["recommended"] is None
