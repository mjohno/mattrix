from __future__ import annotations

import re

import pytest

from .conftest import assessor, complete, coordinator, state, task

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
    assert saved["current"]["validate"]["result"] == "success"
    assert saved["recommended"] == "second"
    assert re.search(
        r"^stagger_step\.[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_]"
        r"[A-Za-z0-9_]*:\d+ \[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\] INFO: ",
        result.stderr,
        re.MULTILINE,
    )
    assert (
        "SIGINT received; interrupt requested at the next STEP boundary"
        in result.stderr
    )
    assert "AFK disabled by Ctrl+C; returning to manual mode" in result.stderr


def test_afk_approves_an_initial_coordinator_blocker(cli):
    run, step, _ = cli
    resolve = complete("resolve-flow-transition")
    resolved_assessment = assessor("resolve-flow-transition")
    resolved_assessment["current_packet"] = resolve
    replies = {
        "coordinator": [
            {
                "lessons": [],
                "proposals": [task("resolve-flow-transition")],
                "recommendation": "resolve-flow-transition",
                "blocked": True,
            },
            coordinator(None),
        ],
        "worker": [{"packet": resolve}],
        "assessor": [resolved_assessment],
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
    assert saved["coordination_blocked"] is False
    assert [entry["slug"] for entry in saved["history"]] == [
        "resolve-flow-transition"
    ]
    assert "## Coordination Blocker" in result.stdout
    assert "AFK enabled" in result.stderr


def test_break_preserves_an_initial_coordinator_blocker(cli):
    run, step, _ = cli
    replies = {
        "coordinator": [
            {
                "lessons": [],
                "proposals": [task("resolve-flow-transition")],
                "recommendation": "resolve-flow-transition",
                "blocked": True,
            }
        ]
    }

    result = run(
        "--log-level",
        "INFO",
        "init",
        "--goal",
        "Goal",
        "--session",
        input="break\n",
        replies=replies,
    )

    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["coordination_blocked"] is True
    assert saved["current"] is None
    assert saved["recommended"] == "resolve-flow-transition"


def test_break_persists_a_later_ordinary_gate(cli):
    run, step, _ = cli
    first = complete("first")
    first_assessed = assessor("first")
    replies = {
        "coordinator": [coordinator("first"), coordinator("second")],
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
        input="approved\nbreak\n",
        replies=replies,
    )

    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["coordination_blocked"] is False
    assert saved["current"]["slug"] == "first"
    assert saved["current"]["validate"]["result"] == "success"
    assert saved["recommended"] == "second"

    resumed = run("session", input="break\n", replies={})

    assert resumed.returncode == 0, resumed.stderr
    assert state(step)["recommended"] == "second"


def test_break_persists_a_later_coordinator_blocker(cli):
    run, step, _ = cli
    first = complete("first")
    first_assessed = assessor("first")
    replies = {
        "coordinator": [
            coordinator("first"),
            {
                "lessons": [],
                "proposals": [task("resolve-flow-transition")],
                "recommendation": "resolve-flow-transition",
                "blocked": True,
            },
        ],
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
        input="approved\nbreak\n",
        replies=replies,
    )

    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["coordination_blocked"] is True
    assert saved["current"]["slug"] == "first"
    assert saved["current"]["validate"]["result"] == "success"
    assert saved["recommended"] == "resolve-flow-transition"


def test_revision_uses_the_coordinator_blocker_value(cli):
    run, step, _ = cli
    replies = {
        "coordinator": [
            {
                "lessons": [],
                "proposals": [task("resolve-flow-transition")],
                "recommendation": "resolve-flow-transition",
                "blocked": True,
            },
            coordinator("revised-flow-transition"),
        ]
    }

    result = run(
        "--log-level",
        "INFO",
        "init",
        "--goal",
        "Goal",
        "--session",
        input="use a revised flow\nbreak\n",
        replies=replies,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.count("## Coordination Blocker") == 1
    assert "### revised-flow-transition" in result.stdout
    assert state(step)["coordination_blocked"] is False


def test_afk_resumes_after_a_validator_blocker(cli):
    run, step, _ = cli
    first = complete("first")
    first["validate"]["result"] = "blocked"
    first_assessed = assessor("first")
    first_assessed["current_packet"] = first
    recover = complete("recover-validation-blocker")
    recovered_assessment = assessor("recover-validation-blocker")
    recovered_assessment["current_packet"] = recover
    replies = {
        "coordinator": [
            coordinator("first"),
            {
                "lessons": [],
                "proposals": [task("recover-validation-blocker")],
                "recommendation": "recover-validation-blocker",
                "blocked": True,
            },
            coordinator(None),
        ],
        "worker": [{"packet": first}, {"packet": recover}],
        "assessor": [first_assessed, recovered_assessment],
    }

    result = run(
        "--log-level",
        "INFO",
        "init",
        "--goal",
        "Goal",
        "--session",
        input="afk\nafk\n",
        replies=replies,
    )

    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["completed"] is True
    assert [entry["slug"] for entry in saved["history"]] == [
        "first",
        "recover-validation-blocker",
    ]
    assert result.stderr.count("AFK enabled") == 2
    assert (
        "AFK disabled by coordinator blocker; returning to manual mode"
        in result.stderr
    )


def test_afk_resumes_until_the_next_coordinator_blocker(cli):
    run, step, _ = cli
    first = complete("first")
    first_assessed = assessor("first")
    resolve = complete("resolve-flow-transition")
    resolved_assessment = assessor("resolve-flow-transition")
    resolved_assessment["current_packet"] = resolve
    replies = {
        "coordinator": [
            coordinator("first"),
            {
                "lessons": [],
                "proposals": [task("resolve-flow-transition")],
                "recommendation": "resolve-flow-transition",
                "blocked": True,
            },
            coordinator(None),
        ],
        "worker": [{"packet": first}, {"packet": resolve}],
        "assessor": [first_assessed, resolved_assessment],
    }

    result = run(
        "--log-level",
        "INFO",
        "init",
        "--goal",
        "Goal",
        "--session",
        input="afk\nafk\n",
        replies=replies,
    )

    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["completed"] is True
    assert saved["coordination_blocked"] is False
    assert [entry["slug"] for entry in saved["history"]] == [
        "first",
        "resolve-flow-transition",
    ]
    assert result.stderr.count("AFK enabled") == 2
    assert (
        "AFK disabled by coordinator blocker; returning to manual mode"
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
    assert saved["current"]["validate"]["result"] == "blocked"
    assert saved["recommended"] == "terminate"
    assert (
        result.stderr.count("AFK automatically approved the current gate") == 1
    )
    assert (
        "AFK disabled by blocked result; returning to manual mode"
        in result.stderr
    )
