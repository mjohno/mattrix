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

    assert (
        PiRpcHarness._read_stdout_line(lines, 1, "timed out")
        == '{"type": "agent_settled"}\n'
    )


def test_stdout_queue_read_times_out():
    lines: queue.Queue[str | None] = queue.Queue()

    with pytest.raises(
        HarnessError, match="RPC idle timed out before settlement"
    ):
        PiRpcHarness._read_stdout_line(
            lines, 0.01, "RPC idle timed out before settlement"
        )


def test_cleanup_escalates_after_bounded_termination(monkeypatch):
    class Pipe:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    class Process:
        def __init__(self):
            self.pid = 123
            self.stdin = Pipe()
            self.stdout = Pipe()
            self.stderr = Pipe()
            self.terminated = False
            self.waits = 0

        def poll(self):
            return None

        def terminate(self):
            self.terminated = True

        def wait(self, timeout):
            self.waits += 1
            if self.waits == 1:
                raise harness.subprocess.TimeoutExpired("pi", timeout)
            return 0

    proc = Process()
    killed = []
    monkeypatch.setattr(
        PiRpcHarness, "_kill_process_tree", lambda _, p: killed.append(p)
    )

    PiRpcHarness()._terminate_process(proc, queue.Queue())

    assert proc.terminated
    assert killed == [proc]
    assert proc.stdin.closed and proc.stdout.closed and proc.stderr.closed


def test_harness_rejects_an_invalid_step_slug_for_pi_naming():
    with pytest.raises(HarnessError, match="STEP file basename"):
        PiRpcHarness(session_scope="/work/STEP-Qual.yaml")
