from __future__ import annotations

import json

import pytest

from .conftest import coordinator, scenario, state

pytestmark = pytest.mark.integration


def init(run, replies=None):
    result = run("init", "--goal", "Goal", replies=replies or scenario("fresh"))
    assert result.returncode == 0, result.stderr


def test_init_persists_ranked_next_and_recommendation(cli):
    run, step, _ = cli
    init(run)
    saved = state(step)
    assert saved["history"] == [] and saved["current"] is None
    assert saved["next"][0]["slug"] == "first" and saved["recommended"] == "first"


def test_harness_session_on_uses_stable_pi_session_id(cli):
    run, _, log = cli
    result = run(
        "--harness-session", "on", "init", "--goal", "Goal", replies=scenario("fresh")
    )
    assert result.returncode == 0, result.stderr
    argv = json.loads(log.read_text().splitlines()[0])["argv"]
    assert "--no-session" not in argv
    assert "--session-id" in argv
    assert len(argv[argv.index("--session-id") + 1]) == 36


def test_gate_approval_promotes_recommended_step(cli):
    run, step, _ = cli
    init(run)
    result = run("gate", "approved", replies=scenario("complete_continue"))
    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["history"] == [] and saved["current"]["slug"] == "first"
    assert saved["current"]["validate"]["result"] == "success"
    assert saved["next"][0]["slug"] == "second" and saved["recommended"] == "second"


def test_gate_approval_prepares_the_promoted_step_before_exit(cli):
    run, step, _ = cli
    init(
        run,
        {
            "coordinator": [
                {
                    "lessons": [],
                    "proposed_next_packets": [
                        {"slug": "first", "intent": "first", "criteria": ["done"]},
                        {"slug": "second", "intent": "second", "criteria": ["done"]},
                    ],
                    "recommendation": "first",
                }
            ]
        },
    )
    result = run("gate", "approved", replies=scenario("complete_continue"))
    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["current"]["slug"] == "first"
    assert saved["current"]["validate"]["result"] == "success"
    assert saved["next"][0]["slug"] == "second" and saved["recommended"] == "second"


def test_gate_prepares_cycle_before_rendering_and_final_signoff(cli):
    run, step, _ = cli
    init(run)
    rendered = run("gate", "approved", replies=scenario("terminal"))
    assert rendered.returncode == 0, rendered.stderr
    saved = state(step)
    assert (
        saved["current"]["slug"] == "first"
        and saved["current"]["validate"]["result"] == "success"
    )
    assert (
        saved["next"] == []
        and saved["recommended"] is None
        and saved["completed"] is False
    )
    signed = run("gate", "approved")
    assert signed.returncode == 0
    saved = state(step)
    assert (
        saved["completed"] is True
        and saved["current"] is None
        and saved["history"][0]["slug"] == "first"
    )


def test_gate_feedback_revises_next_without_promoting_history_or_current(cli):
    run, step, _ = cli
    init(run)
    run("gate", "approved", replies=scenario("complete_continue"))
    before = state(step)
    result = run(
        "gate",
        "use another task",
        replies={"coordinator": [coordinator("third", ["revised lesson"])]},
    )
    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["history"] == before["history"] == []
    assert saved["current"]["slug"] == "first" and saved["next"][0]["slug"] == "third"
    assert saved["recommended"] == "third" and saved["lessons"] == ["revised lesson"]


def test_gate_break_is_non_mutating(cli):
    run, step, _ = cli
    init(run)
    before = step.read_bytes()
    result = run("gate", "break")
    assert result.returncode == 0 and step.read_bytes() == before


def test_session_continues_through_work_cycle_to_final_signoff(cli):
    run, step, _ = cli
    replies = {
        "coordinator": [
            coordinator("first"),
            {
                "lessons": ["terminal lesson"],
                "proposed_next_packets": [],
                "recommendation": None,
            },
        ],
        "worker": [
            {
                "packet": {
                    "slug": "first",
                    "intent": "first",
                    "criteria": ["done"],
                    "do": {"summary": "worked", "evidence": ["file"]},
                    "validate": {"result": "success", "evidence": ["test"]},
                }
            }
        ],
        "assessor": [
            {
                "current_packet": {
                    "slug": "first",
                    "intent": "first",
                    "criteria": ["done"],
                    "do": {"summary": "worked", "evidence": ["file"]},
                    "validate": {"result": "success", "evidence": ["test"]},
                },
                "retro": {"wins": ["progress"], "issues": [], "actions": ["continue"]},
                "clarification_needed": False,
            }
        ],
    }
    result = run(
        "init",
        "--goal",
        "Goal",
        "--session",
        input="approved\napproved\n",
        replies=replies,
    )
    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert (
        saved["completed"] is True
        and saved["current"] is None
        and [entry["slug"] for entry in saved["history"]] == ["first"]
    )
    assert result.stdout.count("recommended:") == 2


def test_session_revision_keeps_running_then_breaks_without_promotion(cli):
    run, step, _ = cli
    replies = {
        "coordinator": [
            coordinator("first"),
            coordinator("second"),
            coordinator("third", ["revised lesson"]),
        ],
        "worker": [
            {
                "packet": {
                    "slug": "first",
                    "intent": "first",
                    "criteria": ["done"],
                    "do": {"summary": "worked", "evidence": ["file"]},
                    "validate": {"result": "success", "evidence": ["test"]},
                }
            }
        ],
        "assessor": [
            {
                "current_packet": {
                    "slug": "first",
                    "intent": "first",
                    "criteria": ["done"],
                    "do": {"summary": "worked", "evidence": ["file"]},
                    "validate": {"result": "success", "evidence": ["test"]},
                },
                "retro": {"wins": ["progress"], "issues": [], "actions": ["continue"]},
                "clarification_needed": False,
            }
        ],
    }
    result = run(
        "init",
        "--goal",
        "Goal",
        "--session",
        input="approved\ntry third\nbreak\n",
        replies=replies,
    )
    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["history"] == [] and saved["current"]["slug"] == "first"
    assert saved["next"][0]["slug"] == "third" and saved["recommended"] == "third"
    assert "STEP response:" not in result.stdout
