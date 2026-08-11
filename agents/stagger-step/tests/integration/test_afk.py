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
    assert result.stdout.count("afk\n\n---\n") == 2
    assert "afk" not in step.read_text().lower()


def test_ctrl_c_during_afk_returns_to_a_manual_unapproved_gate(cli):
    run, step, _ = cli
    replies = {
        "coordinator": [coordinator("first"), coordinator("second")],
        "worker": ["interrupt", {"packet": complete("first")}],
        "assessor": [assessor("first")],
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
    assert saved["history"] == []
    assert saved["current"]["slug"] == "first"
    assert "validate" not in saved["current"]
    assert "INFO " in result.stderr
    assert (
        "SIGINT received; interrupt requested at the next STEP boundary"
        in result.stderr
    )
    assert "AFK disabled by Ctrl+C; returning to manual mode" in result.stderr


def test_afk_stops_at_the_first_blocked_gate(cli):
    run, step, _ = cli
    first = complete("first")
    first["validate"]["result"] = "blocked"
    first_assessed = assessor("first")
    first_assessed["current_packet"] = first
    replies = {
        "coordinator": [coordinator("first"), coordinator(None)],
        "worker": [{"packet": first}],
        "assessor": [first_assessed],
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
    assert saved["history"] == []
    assert saved["current"]["slug"] == "first"
    assert "validate" not in saved["current"]
    assert "AFK automatically approved the current gate" not in result.stderr
    assert (
        "AFK disabled by blocked result; returning to manual mode"
        in result.stderr
    )


def test_afk_allows_one_failure_then_returns_to_manual_break_gate(cli):
    run, step, _ = cli
    first = complete("first")
    first["validate"]["result"] = "failure"
    second = complete("second")
    second["validate"]["result"] = "blocked"
    first_assessed = assessor("first")
    first_assessed["current_packet"] = first
    second_assessed = assessor("second")
    second_assessed["current_packet"] = second
    replies = {
        "coordinator": [
            coordinator("first"),
            coordinator("second"),
            coordinator(None),
        ],
        "worker": [{"packet": first}, {"packet": second}],
        "assessor": [first_assessed, second_assessed],
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
    assert [entry["slug"] for entry in saved["history"]] == ["first"]
    assert saved["current"]["slug"] == "second"
    assert "validate" not in saved["current"]
    assert (
        result.stderr.count("AFK automatically approved the current gate") == 1
    )
    assert (
        "AFK disabled by blocked result; returning to manual mode"
        in result.stderr
    )
