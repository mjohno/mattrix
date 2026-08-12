from __future__ import annotations

from copy import deepcopy

import pytest
import yaml
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
                {"work": {"summary": "implemented", "evidence": ["file"]}}
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
    assert prepared["current"]["work"] == {
        "summary": "implemented",
        "evidence": ["file"],
    }
    assert prepared["current"]["validate"]["result"] == "success"


def test_validator_clarifies_in_its_same_role_session_then_rechecks():
    harness = ScriptHarness(
        {
            "worker": [
                {"work": {"summary": "implemented", "evidence": ["file"]}},
                {
                    "work": {
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
    assert prepared["current"]["work"]["evidence"] == ["file", "command output"]
    assert prepared["current"]["validate"]["result"] == "success"


def test_assessor_records_conflicting_worker_and_validator_clarifications():
    harness = ScriptHarness(
        {
            "worker": [
                {"work": {"summary": "implemented", "evidence": ["file"]}},
                {
                    "work": {
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


@pytest.mark.parametrize(
    ("result", "summary", "action", "slugs"),
    (
        (
            "blocked",
            "Cannot access deployment credentials",
            "Remove the documented credential blocker",
            ("restore-credentials",),
        ),
        (
            "partial",
            "The migration completed but the rollback check failed",
            "Investigate the rollback mismatch",
            ("investigate-rollback", "use-alternate-migration"),
        ),
        (
            "failure",
            "The selected API does not support the required operation",
            "Investigate and replace the failed API approach",
            ("investigate-api-limit", "use-supported-api"),
        ),
    ),
)
def test_coordinator_receives_recovery_evidence_and_persists_ranked_proposals(
    result, summary, action, slugs
):
    proposals = [
        {
            "slug": slug,
            "intent": f"Resolve {slug}",
            "criteria": [f"{slug} evidence exists"],
        }
        for slug in slugs
    ]
    harness = ScriptHarness(
        {
            "worker": [
                {
                    "work": {
                        "summary": "Attempted the approved task",
                        "evidence": ["worker evidence"],
                    }
                }
            ],
            "validator": [
                {
                    "validate": {
                        "result": result,
                        "summary": summary,
                        "evidence": ["validator evidence"],
                    },
                    "clarification_request": None,
                }
            ],
            "assessor": [_retro(issues=[summary], actions=[action])],
            "coordinator": [
                {
                    "lessons": [],
                    "proposals": proposals,
                    "recommendation": slugs[0],
                }
            ],
        }
    )

    prepared = StepLoop(harness).prepare(_state())

    coordinator_prompt = harness.prompts[-1][1]
    assert harness.prompts[-1][0] == "coordinator"
    assert f"result: {result}" in coordinator_prompt
    assert summary in coordinator_prompt
    assert action in coordinator_prompt
    assert [proposal["slug"] for proposal in prepared["next"]] == list(slugs)
    assert prepared["recommended"] == slugs[0]


def test_coordinator_context_partitions_history_and_retains_revision_gate():
    history = [
        {
            "slug": f"task-{index}",
            "intent": f"Task {index}",
            "criteria": ["done"],
            "work": {"summary": f"Worked {index}", "evidence": []},
            "validate": {
                "result": "success",
                "summary": f"Validated {index}",
                "evidence": [],
            },
        }
        for index in range(4)
    ]
    state = create_state("Goal", packet_history=2)
    state.update(
        {
            "history": history,
            "next": [
                {"slug": "proposed", "intent": "Proposed", "criteria": ["done"]}
            ],
            "recommended": "proposed",
        }
    )
    harness = ScriptHarness(
        {
            "coordinator": [
                {
                    "lessons": ["lesson"],
                    "proposals": [
                        {
                            "slug": "future",
                            "intent": "Future",
                            "criteria": ["done"],
                        }
                    ],
                    "recommendation": "future",
                }
            ]
        }
    )

    StepLoop(harness)._propose(state, revision="Change the direction")

    prompt = harness.prompts[0][1]
    context = yaml.safe_load(
        prompt.split("## Invocation context\n\n```yaml\n", 1)[1].split(
            "\n```", 1
        )[0]
    )
    assert "history" not in context
    assert "actions" not in context
    assert [packet["slug"] for packet in context["recent_history"]] == [
        "task-2",
        "task-3",
    ]
    assert context["history_index"] == [
        {"slug": "task-0", "result": "success", "summary": "Validated 0"},
        {"slug": "task-1", "result": "success", "summary": "Validated 1"},
    ]
    assert context["current_gate"] is None
    assert context["proposals"] == state["next"]
    assert context["recommended"] == "proposed"
    assert context["completed"] is False
    assert context["revision"] == "Change the direction"
