from __future__ import annotations

from copy import deepcopy

from stagger_step.loop import StepLoop
from stagger_step.state import create_state


class ScriptHarness:
    def __init__(self, replies):
        self.replies = {role: list(values) for role, values in replies.items()}
        self.calls = []
        self.prompts = []

    def begin_transition(self):
        self.calls.append(("begin", False))

    def invoke(self, role, prompt, *, task_slug="bootstrap", follow_up=False):
        self.calls.append((role, follow_up))
        self.prompts.append((role, prompt))
        return deepcopy(self.replies[role].pop(0))


def _state():
    state = create_state("Goal")
    state["current"] = {
        "slug": "first",
        "intent": "First",
        "criteria": ["done"],
    }
    return state


def _retro(requests=None, issues=None, actions=None):
    return {
        "retro": {
            "wins": ["progress"],
            "issues": issues or [],
            "actions": actions or ["continue"],
        },
        "clarification_requests": requests or [],
    }


def _coordinator():
    return {"lessons": [], "proposals": [], "recommendation": "terminate"}


def test_prepare_runs_independent_validator_before_assessor():
    harness = ScriptHarness(
        {
            "worker": [
                {"do": {"summary": "implemented", "evidence": ["file"]}}
            ],
            "validator": [
                {
                    "validate": {
                        "result": "success",
                        "summary": "checked",
                        "evidence": ["test"],
                    },
                    "clarification_request": None,
                }
            ],
            "assessor": [_retro()],
            "coordinator": [_coordinator()],
        }
    )

    prepared = StepLoop(harness).prepare(_state())

    assert [role for role, _ in harness.calls] == [
        "begin",
        "worker",
        "validator",
        "assessor",
        "coordinator",
    ]
    assert prepared["current"]["do"] == {
        "summary": "implemented",
        "evidence": ["file"],
    }
    assert prepared["current"]["validate"]["result"] == "success"


def test_validator_clarifies_in_its_same_role_session_then_rechecks():
    harness = ScriptHarness(
        {
            "worker": [
                {"do": {"summary": "implemented", "evidence": ["file"]}},
                {
                    "do": {
                        "summary": "more evidence",
                        "evidence": ["command output"],
                    }
                },
            ],
            "validator": [
                {
                    "validate": {
                        "result": "partial",
                        "summary": "need output",
                        "evidence": [],
                    },
                    "clarification_request": "Provide command output.",
                },
                {
                    "validate": {
                        "result": "success",
                        "summary": "checked",
                        "evidence": ["output"],
                    },
                    "clarification_request": None,
                },
            ],
            "assessor": [_retro()],
            "coordinator": [_coordinator()],
        }
    )

    prepared = StepLoop(harness).prepare(_state())

    assert harness.calls[3:5] == [("worker", True), ("validator", True)]
    assert prepared["current"]["do"]["evidence"] == ["file", "command output"]
    assert prepared["current"]["validate"]["result"] == "success"


def test_assessor_records_conflicting_worker_and_validator_clarifications():
    harness = ScriptHarness(
        {
            "worker": [
                {"do": {"summary": "implemented", "evidence": ["file"]}},
                {
                    "do": {
                        "summary": "deployment evidence",
                        "evidence": ["release version v2 is active"],
                    }
                },
            ],
            "validator": [
                {
                    "validate": {
                        "result": "partial",
                        "summary": "checked",
                        "evidence": ["test"],
                    },
                    "clarification_request": None,
                },
                {
                    "validate": {
                        "result": "partial",
                        "summary": "deployment result",
                        "evidence": ["release version v1 remains active"],
                    },
                    "clarification_request": None,
                },
            ],
            "assessor": [
                _retro(
                    [
                        {
                            "target": "worker",
                            "request": "Show delivery evidence.",
                        },
                        {
                            "target": "validator",
                            "request": "Explain partial result.",
                        },
                    ]
                ),
                _retro(
                    issues=["evidence conflict"], actions=["resolve conflict"]
                ),
            ],
            "coordinator": [_coordinator()],
        }
    )

    prepared = StepLoop(harness).prepare(_state())

    assert harness.calls == [
        ("begin", False),
        ("worker", False),
        ("validator", False),
        ("assessor", False),
        ("worker", True),
        ("validator", True),
        ("assessor", True),
        ("coordinator", False),
    ]
    assert prepared["current"]["validate"]["summary"] == "checked"
    assert [
        item["target"] for item in prepared["current"]["clarifications"]
    ] == ["worker", "validator"]
    assert prepared["current"]["retro"] == {
        "wins": ["progress"],
        "issues": ["evidence conflict"],
        "actions": ["resolve conflict"],
    }
    assessor_follow_up_prompt = harness.prompts[6][1]
    assert "release version v2 is active" in assessor_follow_up_prompt
    assert "release version v1 remains active" in assessor_follow_up_prompt
