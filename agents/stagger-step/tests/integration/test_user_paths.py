from __future__ import annotations

import json
import re

import pytest
from stagger_step.harness import HarnessError, PiRpcHarness

from .conftest import (
    FAKE,
    assessor,
    calls,
    complete,
    coordinator,
    scenario,
    state,
)

pytestmark = pytest.mark.integration


def init(run, replies=None):
    result = run("init", "--goal", "Goal", replies=replies or scenario("fresh"))
    assert result.returncode == 0, result.stderr


def test_init_persists_ranked_next_and_recommendation(cli):
    run, step, _ = cli
    init(run)
    saved = state(step)
    assert saved["history"] == [] and saved["current"] is None
    assert (
        saved["next"][0]["slug"] == "first" and saved["recommended"] == "first"
    )


def test_default_harness_sessions_are_named_logged_and_keep_state_clean(cli):
    run, step, log = cli
    result = run(
        "--log-level",
        "INFO",
        "init",
        "--goal",
        "Goal",
        replies=scenario("fresh"),
    )
    assert result.returncode == 0, result.stderr
    argv = json.loads(log.read_text().splitlines()[0])["argv"]
    assert "--no-session" not in argv
    assert "--session-id" in argv
    assert len(argv[argv.index("--session-id") + 1]) == 36
    assert argv[argv.index("--name") + 1] == "STEP-qual-bootstrap-coordinator"
    assert "--extension" in argv
    assert argv[argv.index("--extension") + 1].endswith("pi_extension/index.ts")
    assert argv[argv.index("--step-role") + 1] == "coordinator"
    assert (
        "Call `stagger_step_finalize_coordinator` exactly once"
        in json.loads(log.read_text().splitlines()[0])["prompt"]
    )
    assert re.search(
        r"^INFO \[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\] "
        r"stagger_step\.harness: pi role session started",
        result.stderr,
        re.MULTILINE,
    )
    assert "session_name=STEP-qual-bootstrap-coordinator" in result.stderr
    assert "session_id=" in result.stderr
    assert "session" not in step.read_text()


def test_debug_logs_buffer_thinking_without_raw_rpc_events(cli):
    run, _, _ = cli
    replies = {
        "coordinator": [
            {
                **coordinator("first"),
                "_thinking": "Inspecting\nthe current state.",
            }
        ]
    }

    result = run(
        "--log-level", "DEBUG", "init", "--goal", "Goal", replies=replies
    )

    assert result.returncode == 0, result.stderr
    assert re.search(
        r"^DEBUG \[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\] "
        r"stagger_step\.harness: pi thinking end role=coordinator "
        r"task=bootstrap content_index=0 output=Inspecting the current state\.$",
        result.stderr,
        re.MULTILINE,
    )
    assert "pi rpc stdout" not in result.stderr
    assert '"type": "thinking_delta"' not in result.stderr


def test_harness_session_off_uses_no_session(cli):
    run, _, log = cli
    result = run(
        "--harness-session",
        "off",
        "init",
        "--goal",
        "Goal",
        replies=scenario("fresh"),
    )
    assert result.returncode == 0, result.stderr
    argv = json.loads(log.read_text().splitlines()[0])["argv"]
    assert "--no-session" in argv
    assert "--session-id" not in argv


def test_gate_approval_promotes_recommended_step(cli):
    run, step, _ = cli
    init(run)
    result = run("gate", "approved", replies=scenario("complete_continue"))
    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["history"] == [] and saved["current"]["slug"] == "first"
    assert saved["current"]["validate"]["result"] == "success"
    assert (
        saved["next"][0]["slug"] == "second"
        and saved["recommended"] == "second"
    )


def test_invalid_worker_packet_is_corrected_in_its_persistent_session(cli):
    run, step, log = cli
    init(run)
    invalid = {
        "packet": {"slug": "first", "intent": "first", "criteria": ["done"]}
    }
    result = run(
        "gate",
        "approved",
        replies={
            "worker": [invalid, {"packet": complete("first")}],
            "assessor": [assessor("first")],
            "coordinator": [coordinator("second")],
        },
    )
    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["current"]["slug"] == "first"
    worker_calls = [
        json.loads(line)
        for line in log.read_text().splitlines()
        if '"role": "worker"' in line
    ]
    assert len(worker_calls) == 2
    assert "worker.do must be a mapping" in worker_calls[1]["prompt"]
    assert "worker finalizer" in worker_calls[1]["prompt"]
    assert (
        worker_calls[0]["argv"][
            worker_calls[0]["argv"].index("--session-id") + 1
        ]
        == worker_calls[1]["argv"][
            worker_calls[1]["argv"].index("--session-id") + 1
        ]
    )


def test_loop_preserves_approved_task_identity_without_worker_input(cli):
    run, step, _ = cli
    init(run)
    result = run(
        "gate",
        "approved",
        replies={
            "worker": [{"packet": complete("different-task")}],
            "assessor": [assessor("first")],
            "coordinator": [coordinator("second")],
        },
    )

    assert result.returncode == 0, result.stderr
    assert state(step)["current"]["intent"] == "first"


def test_loop_preserves_worker_result_without_assessor_input(cli):
    run, step, _ = cli
    init(run)
    worker = complete("first")
    worker["validate"]["result"] = "partial"
    result = run(
        "gate",
        "approved",
        replies={
            "worker": [{"packet": worker}],
            "assessor": [assessor("first")],
            "coordinator": [coordinator("second")],
        },
    )

    assert result.returncode == 0, result.stderr
    assert state(step)["current"]["validate"]["result"] == "partial"


def test_clarification_preserves_approved_task_identity(cli):
    run, step, _ = cli
    init(run)
    result = run(
        "gate",
        "approved",
        replies={
            "worker": [
                {"packet": complete("first")},
                {"packet": complete("different-task")},
            ],
            "assessor": [assessor("first", clarify=True), assessor("first")],
            "coordinator": [coordinator("second")],
        },
    )

    assert result.returncode == 0, result.stderr
    assert state(step)["current"]["slug"] == "first"


def test_missing_coordinator_finalizer_is_repaired_in_the_same_role_session(
    cli,
):
    run, step, log = cli
    result = run(
        "init",
        "--goal",
        "Goal",
        replies={"coordinator": ["no_finalizer", coordinator("first")]},
    )
    assert result.returncode == 0, result.stderr
    coordinator_calls = [
        call for call in calls(log) if call["role"] == "coordinator"
    ]
    assert len(coordinator_calls) == 2
    assert (
        "Finalize the current STEP role result"
        in coordinator_calls[1]["prompt"]
    )
    assert "## Invocation context" not in coordinator_calls[1]["prompt"]
    assert (
        coordinator_calls[0]["argv"][
            coordinator_calls[0]["argv"].index("--session-id") + 1
        ]
        == coordinator_calls[1]["argv"][
            coordinator_calls[1]["argv"].index("--session-id") + 1
        ]
    )
    assert state(step)["next"][0]["slug"] == "first"


def test_missing_finalizer_is_repaired_in_the_same_role_session(cli):
    run, step, log = cli
    init(run)
    result = run(
        "gate",
        "approved",
        replies={
            "worker": ["no_finalizer", {"packet": complete("first")}],
            "assessor": [assessor("first")],
            "coordinator": [coordinator("second")],
        },
    )
    assert result.returncode == 0, result.stderr
    worker_calls = [
        json.loads(line)
        for line in log.read_text().splitlines()
        if '"role": "worker"' in line
    ]
    assert len(worker_calls) == 2
    assert "Finalize the current STEP role result" in worker_calls[1]["prompt"]
    assert "## Invocation context" not in worker_calls[1]["prompt"]
    saved = state(step)
    assert saved["current"]["slug"] == "first"


def test_missing_assessor_finalizer_is_repaired_in_the_same_role_session(cli):
    run, step, log = cli
    init(run)
    result = run(
        "gate",
        "approved",
        replies={
            "worker": [{"packet": complete("first")}],
            "assessor": ["no_finalizer", assessor("first")],
            "coordinator": [coordinator("second")],
        },
    )
    assert result.returncode == 0, result.stderr
    assessor_calls = [call for call in calls(log) if call["role"] == "assessor"]
    assert len(assessor_calls) == 2
    assert (
        "Finalize the current STEP role result" in assessor_calls[1]["prompt"]
    )
    assert "## Invocation context" not in assessor_calls[1]["prompt"]
    assert (
        assessor_calls[0]["argv"][
            assessor_calls[0]["argv"].index("--session-id") + 1
        ]
        == assessor_calls[1]["argv"][
            assessor_calls[1]["argv"].index("--session-id") + 1
        ]
    )
    assert state(step)["current"]["slug"] == "first"


def test_repeated_close_retries_and_keeps_step_state_unchanged(cli):
    run, step, log = cli
    init(run)
    before = step.read_bytes()
    result = run(
        "gate", "approved", replies={"worker": ["close", "close", "close"]}
    )
    assert result.returncode == 3
    assert "RPC closed before settlement" in result.stderr
    assert len([call for call in calls(log) if call["role"] == "worker"]) == 3
    assert step.read_bytes() == before


def test_wrong_finalizer_is_rejected_without_step_state_mutation(cli):
    run, step, log = cli
    init(run)
    before = step.read_bytes()
    result = run(
        "gate",
        "approved",
        replies={"worker": ["wrong_finalizer", "wrong_finalizer"]},
    )
    assert result.returncode == 3
    assert "without stagger_step_finalize_worker" in result.stderr
    assert len([call for call in calls(log) if call["role"] == "worker"]) == 2
    assert step.read_bytes() == before


def test_timeout_retries_against_fake_pi(tmp_path, monkeypatch):
    scenario_path = tmp_path / "scenario.json"
    log_path = tmp_path / "pi.log"
    scenario_path.write_text(json.dumps({"worker": ["sleep", "sleep"]}))
    monkeypatch.setenv("FAKE_PI_SCENARIO", str(scenario_path))
    monkeypatch.setenv("FAKE_PI_LOG", str(log_path))
    harness = PiRpcHarness(
        command=(str(FAKE),),
        timeout_seconds=0.2,
        retries=1,
        session_enabled=False,
    )

    with pytest.raises(
        HarnessError, match="RPC idle timed out before settlement"
    ):
        harness.invoke("worker", "test timeout")

    retry = calls(log_path)[1]["prompt"]
    assert "Continue the current STEP role session" in retry
    assert "idle period passed" in retry
    assert "test timeout" not in retry


def test_activity_resets_the_rpc_idle_timeout(tmp_path, monkeypatch):
    scenario_path = tmp_path / "scenario.json"
    log_path = tmp_path / "pi.log"
    scenario_path.write_text(json.dumps({"worker": ["heartbeat"]}))
    monkeypatch.setenv("FAKE_PI_SCENARIO", str(scenario_path))
    monkeypatch.setenv("FAKE_PI_LOG", str(log_path))
    harness = PiRpcHarness(
        command=(str(FAKE),),
        timeout_seconds=0.15,
        max_invocation_seconds=1,
        retries=0,
        session_enabled=False,
    )

    with pytest.raises(HarnessError, match="RPC closed before settlement"):
        harness.invoke("worker", "test activity")


def test_second_missing_finalizer_keeps_step_state_unchanged(cli):
    run, step, _ = cli
    init(run)
    before = step.read_bytes()
    result = run(
        "gate", "approved", replies={"worker": ["no_finalizer", "no_finalizer"]}
    )
    assert result.returncode == 3
    assert "without stagger_step_finalize_worker" in result.stderr
    assert step.read_bytes() == before


def test_second_invalid_worker_packet_keeps_step_state_unchanged(cli):
    run, step, _ = cli
    init(run)
    before = step.read_bytes()
    invalid = {
        "packet": {"slug": "first", "intent": "first", "criteria": ["done"]}
    }
    result = run(
        "gate", "approved", replies={"worker": [invalid, {"packet": "invalid"}]}
    )
    assert result.returncode == 2
    assert "worker.do must be a mapping" in result.stderr
    assert step.read_bytes() == before


def test_duplicate_next_slug_is_renamed_after_approval(cli):
    run, step, _ = cli
    init(run)
    replies = {
        "worker": [{"packet": complete("first")}],
        "assessor": [assessor("first")],
        "coordinator": [coordinator("first")],
    }
    result = run("gate", "approved", replies=replies)
    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["current"]["slug"] == "first"
    assert saved["next"][0]["slug"] == "first-1"
    assert saved["recommended"] == "first-1"


def test_gate_approval_prepares_the_promoted_step_before_exit(cli):
    run, step, _ = cli
    init(
        run,
        {
            "coordinator": [
                {
                    "lessons": [],
                    "proposed_next_packets": [
                        {
                            "slug": "first",
                            "intent": "first",
                            "criteria": ["done"],
                        },
                        {
                            "slug": "second",
                            "intent": "second",
                            "criteria": ["done"],
                        },
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
    assert (
        saved["next"][0]["slug"] == "second"
        and saved["recommended"] == "second"
    )


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
    assert (
        saved["current"]["slug"] == "first"
        and saved["next"][0]["slug"] == "third"
    )
    assert saved["recommended"] == "third" and saved["lessons"] == [
        "revised lesson"
    ]


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
                    "validate": {
                        "result": "success",
                        "summary": "Ran tests",
                        "evidence": ["test"],
                    },
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
                    "validate": {
                        "result": "success",
                        "summary": "Ran tests",
                        "evidence": ["test"],
                    },
                },
                "retro": {
                    "wins": ["progress"],
                    "issues": [],
                    "actions": ["continue"],
                },
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
                    "validate": {
                        "result": "success",
                        "summary": "Ran tests",
                        "evidence": ["test"],
                    },
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
                    "validate": {
                        "result": "success",
                        "summary": "Ran tests",
                        "evidence": ["test"],
                    },
                },
                "retro": {
                    "wins": ["progress"],
                    "issues": [],
                    "actions": ["continue"],
                },
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
    assert (
        saved["next"][0]["slug"] == "third" and saved["recommended"] == "third"
    )
    assert "STEP response:" not in result.stdout


def test_init_persists_change_path_and_supplies_it_to_each_role(cli):
    run, step, log = cli
    artifacts = step.parent / "artifacts"
    artifacts.mkdir()
    result = run(
        "init",
        "--goal",
        "Goal",
        "--change",
        "artifacts",
        replies=scenario("fresh"),
    )
    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["change_path"] == "artifacts"
    assert saved["commit_mode"] is False

    result = run("gate", "approved", replies=scenario("complete_continue"))
    assert result.returncode == 0, result.stderr
    role_calls = [
        call
        for call in calls(log)
        if call["role"] in {"worker", "assessor", "coordinator"}
    ]
    assert {call["role"] for call in role_calls} == {
        "worker",
        "assessor",
        "coordinator",
    }
    for call in role_calls:
        assert "## Change path" in call["prompt"]
        assert f"`{artifacts.resolve()}`" in call["prompt"]


def test_init_rejects_missing_change_path(cli):
    run, _, _ = cli

    result = run("init", "--goal", "Goal", "--change", "missing")

    assert result.returncode == 2
    assert "change_path must name an existing directory" in result.stderr


def test_removed_change_path_fails_before_role_invocation(cli):
    run, step, log = cli
    artifacts = step.parent / "artifacts"
    artifacts.mkdir()
    result = run(
        "init",
        "--goal",
        "Goal",
        "--change",
        "artifacts",
        replies={"coordinator": [coordinator("first")]},
    )
    assert result.returncode == 0, result.stderr
    artifacts.rmdir()

    result = run(
        "gate", "approved", replies={"worker": [{"packet": complete("first")}]}
    )

    assert result.returncode == 2
    assert "change_path must name an existing directory" in result.stderr
    assert not log.exists()
