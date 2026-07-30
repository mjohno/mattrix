from __future__ import annotations

import pytest

from stagger_step.harness import HarnessError, PiRpcHarness


def test_harness_rejects_an_invalid_step_slug_for_pi_naming():
    with pytest.raises(HarnessError, match="STEP file basename"):
        PiRpcHarness(session_scope="/work/STEP-Qual.yaml")
