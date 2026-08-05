from __future__ import annotations

import pytest
from stagger_step.prompts import (
    build_continuation_prompt,
    build_finalization_prompt,
    build_prompt,
)


def test_retry_prompts_target_continuation_or_finalization():
    continuation = build_continuation_prompt("worker")
    finalization = build_finalization_prompt(
        "worker", ValueError("missing packet")
    )

    assert "idle period passed" in continuation
    assert "Do not restart" in continuation
    assert "Finalize the current STEP role result" in finalization
    assert "Do not resume implementation" in finalization
    assert "missing packet" in finalization
    assert "stagger_step_finalize_worker" in continuation
    assert "stagger_step_finalize_worker" in finalization
    assert "## Invocation context" not in continuation
    assert "## Invocation context" not in finalization


@pytest.mark.parametrize(
    ("role", "role_title", "finalizer"),
    (
        ("coordinator", "# Coordinator", "stagger_step_finalize_coordinator"),
        ("worker", "# Team Member", "stagger_step_finalize_worker"),
        ("assessor", "# Delivery Manager", "stagger_step_finalize_assessor"),
    ),
)
def test_role_prompt_is_self_contained_and_role_specific(
    role: str, role_title: str, finalizer: str
):
    prompt = build_prompt(role, {"goal": "Ship the change"})

    assert "# Stagger Step Team" in prompt
    assert "STEP.goal" in prompt
    assert "**Owner**" in prompt
    assert role_title in prompt
    assert finalizer in prompt
    assert "skills/" not in prompt
    assert "/skill:" not in prompt
    assert "## Invocation context" in prompt


def test_coordinator_embeds_bounded_task_guidance():
    prompt = build_prompt("coordinator", {"goal": "Ship the change"})

    assert "bounded, actionable outcome" in prompt
    assert "independent, negotiable, small, and testable" in prompt


def test_worker_and_assessor_preserve_failure_learning():
    worker = build_prompt("worker", {"goal": "Ship the change"})
    assessor = build_prompt("assessor", {"goal": "Ship the change"})

    assert "evidence of both success and failure" in worker
    assert "credible failure evidence as delivery learning" in assessor


def test_unknown_role_is_rejected():
    with pytest.raises(ValueError, match="unknown STEP role"):
        build_prompt("owner", {})
