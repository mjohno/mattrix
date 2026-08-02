from __future__ import annotations

import pytest

from stagger_step import harness
from stagger_step.harness import HarnessError, PiRpcHarness


def test_default_harness_command_uses_windows_pi_shim(monkeypatch):
    monkeypatch.setattr(harness.os, "name", "nt")

    assert PiRpcHarness().command == ("pi.cmd", "--mode", "rpc", "--no-session")


def test_windows_pipe_read_does_not_use_select(monkeypatch):
    class Stream:
        def readline(self):
            return '{"type": "agent_settled"}\n'

    def unexpected_select(*args):
        raise AssertionError("Windows pipe reads must not use select")

    monkeypatch.setattr(harness.os, "name", "nt")
    monkeypatch.setattr(harness.select, "select", unexpected_select)

    assert (
        PiRpcHarness._read_stdout_line(Stream(), 1)
        == '{"type": "agent_settled"}\n'
    )


def test_harness_rejects_an_invalid_step_slug_for_pi_naming():
    with pytest.raises(HarnessError, match="STEP file basename"):
        PiRpcHarness(session_scope="/work/STEP-Qual.yaml")
