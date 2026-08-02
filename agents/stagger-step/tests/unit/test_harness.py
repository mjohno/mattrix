from __future__ import annotations

import queue

import pytest

from stagger_step import harness
from stagger_step.harness import HarnessError, PiRpcHarness


def test_default_harness_command_uses_windows_pi_shim(monkeypatch):
    monkeypatch.setattr(harness.os, "name", "nt")

    assert PiRpcHarness().command == ("pi.cmd", "--mode", "rpc", "--no-session")


def test_stdout_queue_read_returns_a_line():
    lines: queue.Queue[str | None] = queue.Queue()
    lines.put('{"type": "agent_settled"}\n')

    assert PiRpcHarness._read_stdout_line(lines, 1) == '{"type": "agent_settled"}\n'


def test_stdout_queue_read_times_out():
    lines: queue.Queue[str | None] = queue.Queue()

    with pytest.raises(HarnessError, match="RPC timed out before settlement"):
        PiRpcHarness._read_stdout_line(lines, 0.01)


def test_harness_rejects_an_invalid_step_slug_for_pi_naming():
    with pytest.raises(HarnessError, match="STEP file basename"):
        PiRpcHarness(session_scope="/work/STEP-Qual.yaml")
