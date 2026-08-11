from __future__ import annotations

import pytest
from stagger_step.prompts import build_finalization_prompt, build_prompt


def test_finalization_retry_prompt_targets_prior_session_result():
    finalization = build_finalization_prompt(
        "worker", ValueError("missing packet")
    )

    assert "Finalize the current STEP role result" in finalization
    assert "Do not resume implementation" in finalization
    assert "missing packet" in finalization
    assert "stagger_step_finalize_worker" in finalization
    assert "with its required typed arguments" in finalization
    assert "## Invocation context" not in finalization


@pytest.mark.parametrize(
    ("role", "role_title", "finalizer"),
    (
        ("coordinator", "# Coordinator", "stagger_step_finalize_coordinator"),
        ("worker", "# Worker", "stagger_step_finalize_worker"),
        ("validator", "# Validator", "stagger_step_finalize_validator"),
        ("assessor", "# Assessor", "stagger_step_finalize_assessor"),
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
    assert "with its required typed arguments" in prompt
    assert "For example:" in prompt


def test_role_prompt_includes_active_change_path_only_when_supplied():
    without_path = build_prompt("worker", {"goal": "Ship the change"})
    with_path = build_prompt(
        "worker", {"goal": "Ship the change"}, "/tmp/change-artifacts"
    )

    assert "## Change path" not in without_path
    assert "## Change path" in with_path
    assert "`/tmp/change-artifacts`" in with_path
    assert "not a security boundary" in with_path
    assert "CHANGE.md" not in with_path


def test_coordinator_embeds_bounded_task_guidance():
    prompt = build_prompt("coordinator", {"goal": "Ship the change"})

    assert "bounded, actionable outcome" in prompt
    assert "independent, negotiable, small, and testable" in prompt


def test_coordinator_guides_recovery_planning():
    prompt = build_prompt("coordinator", {"goal": "Ship the change"})

    assert "smallest practical task that removes it" in prompt
    assert "bounded task that obtains the evidence" in prompt
    assert "partial` or `failure" in prompt
    assert "Do not repeat a failed or blocked approach" in prompt
    assert "exactly one next task" in prompt


def test_role_prompts_preserve_evidence_boundaries():
    worker = build_prompt("worker", {"goal": "Ship the change"})
    validator = build_prompt("validator", {"goal": "Ship the change"})
    assessor = build_prompt("assessor", {"goal": "Ship the change"})

    assert "Do not validate the task" in worker
    assert "Report evidence of both success and failure" in validator
    assert "credible failure evidence as delivery learning" in assessor


def test_unknown_role_is_rejected():
    with pytest.raises(ValueError, match="unknown STEP role"):
        build_prompt("owner", {})
