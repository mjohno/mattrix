from __future__ import annotations

import pytest

from stagger_step import harness
from stagger_step.harness import HarnessError, PiRpcHarness


def test_default_harness_command_uses_windows_pi_shim(monkeypatch):
    monkeypatch.setattr(harness.os, "name", "nt")

    assert PiRpcHarness().command == ("pi.cmd", "--mode", "rpc", "--no-session")


def test_harness_rejects_an_invalid_step_slug_for_pi_naming():
    with pytest.raises(HarnessError, match="STEP file basename"):
        PiRpcHarness(session_scope="/work/STEP-Qual.yaml")
