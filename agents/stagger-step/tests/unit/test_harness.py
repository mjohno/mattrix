from __future__ import annotations

import pytest

from stagger_step.harness import HarnessError, PiRpcHarness


def test_role_session_ids_are_deterministic_and_role_specific():
    harness = PiRpcHarness(session_scope="/work/STEP-qual.yaml")

    assert harness._session_id("worker") == harness._session_id("worker")
    assert harness._session_id("worker") != harness._session_id("assessor")
    assert harness._session_name("worker") == "STEP-qual-worker"


def test_harness_rejects_invalid_step_filename_for_pi_naming():
    with pytest.raises(HarnessError, match="lowercase kebab-case"):
        PiRpcHarness(session_scope="/work/STEP-Qual.yaml")
