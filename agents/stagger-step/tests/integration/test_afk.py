from __future__ import annotations

import pytest

from .conftest import assessor, complete, coordinator, state

pytestmark = pytest.mark.integration


def test_afk_approves_subsequent_gate_and_never_persists_mode(cli):
    run, step, _ = cli
    replies = {
        "coordinator": [
            coordinator("first"),
            coordinator(None, ["terminal lesson"]),
        ],
        "worker": [{"packet": complete("first")}],
        "assessor": [assessor("first")],
    }

    result = run(
        "--log-level",
        "INFO",
        "init",
        "--goal",
        "Goal",
        "--session",
        input="afk\n",
        replies=replies,
    )

    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["completed"] is True
    assert [entry["slug"] for entry in saved["history"]] == ["first"]
    assert "AFK enabled" in result.stderr
    assert "AFK automatically approved the current gate" in result.stderr
    assert "afk" not in step.read_text().lower()


def test_afk_failure_returns_to_manual_break_gate(cli):
    run, step, _ = cli
    failed = complete("first")
    failed["validate"]["result"] = "failure"
    assessed = assessor("first")
    assessed["current_packet"] = failed
    replies = {
        "coordinator": [coordinator("first"), coordinator("second")],
        "worker": [{"packet": failed}],
        "assessor": [assessed],
    }

    result = run(
        "--log-level",
        "INFO",
        "init",
        "--goal",
        "Goal",
        "--session",
        input="afk\nbreak\n",
        replies=replies,
    )

    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["completed"] is False
    assert saved["history"] == []
    assert saved["current"]["validate"]["result"] == "failure"
    assert "AFK disabled by failure threshold" in result.stderr
