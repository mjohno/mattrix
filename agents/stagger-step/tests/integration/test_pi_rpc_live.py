"""Opt-in compatibility check against an installed real Pi RPC server."""
from __future__ import annotations
import os
import pytest
from stagger_step.harness import PiRpcHarness
pytestmark = [pytest.mark.integration, pytest.mark.live, pytest.mark.skipif(os.getenv("PI_RPC_INTEGRATION") != "1", reason="set PI_RPC_INTEGRATION=1")]
def test_real_pi_rpc_adapter_returns_role_yaml():
    payload = PiRpcHarness(timeout_seconds=120, retries=0).invoke("coordinator", "Return exactly this YAML and nothing else:\nlessons: []\nproposed_next_packets: []\nrecommendation: null")
    assert payload == {"lessons": [], "proposed_next_packets": [], "recommendation": None}
