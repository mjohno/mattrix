from __future__ import annotations

import pytest
from stagger_step.loop import StepLoop

pytestmark = pytest.mark.integration


def test_approval_consumes_the_promoted_step_and_clears_recommendation():
    """Cover the local StepLoop-to-state transition boundary."""

    class NoHarness:
        pass

    task = {
        "slug": "task",
        "intent": "Task",
        "criteria": ["done"],
    }
    first, second = {**task, "slug": "first"}, {**task, "slug": "second"}
    state = {
        "version": 1,
        "goal": "Goal",
        "change_path": None,
        "commit_mode": False,
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


def test_gate_exposes_next_steps_as_proposals():
    """Keep the human-facing gate aligned with coordinator packets."""

    class NoHarness:
        pass

    proposal = {"slug": "task", "intent": "Task", "criteria": ["done"]}
    state = {
        "version": 1,
        "goal": "Goal",
        "change_path": None,
        "commit_mode": False,
        "lessons": [],
        "history": [],
        "current": None,
        "next": [proposal],
        "recommended": "task",
        "completed": False,
    }

    gate = StepLoop(NoHarness()).gate(state)

    assert gate["proposals"] == [proposal]
    assert "next" not in gate
