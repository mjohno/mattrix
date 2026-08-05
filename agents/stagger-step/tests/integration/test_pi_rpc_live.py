"""Opt-in Pi-facing live black-box smoke check against installed Pi RPC.

Run after focused units and deterministic local integration coverage; it requires
PI_RPC_INTEGRATION=1 and must not be needed for ordinary local test runs.
"""

from __future__ import annotations

import os

import pytest
from stagger_step.harness import PiRpcHarness

pytestmark = [
    pytest.mark.integration,
    pytest.mark.live,
    pytest.mark.skipif(
        os.getenv("PI_RPC_INTEGRATION") != "1",
        reason="set PI_RPC_INTEGRATION=1",
    ),
]


def test_real_pi_rpc_adapter_returns_typed_coordinator_json():
    payload = PiRpcHarness(timeout_seconds=120, retries=0).invoke(
        "coordinator",
        "Call stagger_step_finalize_coordinator exactly once with "
        "lessons=[], proposals=[], and recommendation=null. "
        "Do not return a YAML packet in assistant text.",
    )
    assert payload == {
        "lessons": [],
        "proposed_next_packets": [],
        "recommendation": None,
    }
