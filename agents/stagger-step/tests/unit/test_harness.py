from __future__ import annotations

import logging

import pytest

from stagger_step.harness import HarnessError, PiRpcHarness


def test_role_sessions_are_role_isolated_and_transition_scoped(caplog):
    caplog.set_level(logging.INFO, logger="stagger_step.harness")
    harness = PiRpcHarness(session_scope="/work/STEP-qual.yaml")

    worker_id = harness._session_id("worker", "validate-cli")
    assert worker_id == harness._session_id("worker", "validate-cli")
    assert worker_id != harness._session_id("assessor", "validate-cli")
    assert harness._session_name("worker", "validate-cli") == (
        "STEP-qual-validate-cli-worker"
    )
    assert (
        harness._session_name("coordinator")
        == "STEP-qual-bootstrap-coordinator"
    )

    harness.begin_transition()

    assert worker_id != harness._session_id("worker", "validate-cli")
    messages = [record.getMessage() for record in caplog.records]
    assert any(
        "session_name=STEP-qual-validate-cli-worker" in message
        and f"session_id={worker_id}" in message
        for message in messages
    )


def test_packaged_pi_extension_is_available():
    extension = PiRpcHarness._extension_path()

    assert extension.name == "index.ts"
    assert extension.parent.name == "pi_extension"
    assert extension.is_file()


def test_harness_rejects_invalid_step_or_task_slug_for_pi_naming():
    with pytest.raises(HarnessError, match="STEP file basename"):
        PiRpcHarness(session_scope="/work/STEP-Qual.yaml")

    harness = PiRpcHarness(session_scope="/work/STEP-qual.yaml")
    with pytest.raises(HarnessError, match="task slug"):
        harness._session_name("worker", "Validate CLI")
