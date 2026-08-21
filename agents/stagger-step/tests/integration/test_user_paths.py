from __future__ import annotations

import json
import logging
import re

import pytest
import yaml
from stagger_step.harness import HarnessError, PiRpcHarness
from stagger_step.state import load_state

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
    result = run("init", "--goal", "Goal")
    assert result.returncode == 0, result.stderr
    result = run("gate", replies=replies or scenario("fresh"))
    assert result.returncode == 0, result.stderr


def test_init_persists_unstarted_state_without_coordinator_execution(cli):
    run, step, log = cli
    result = run("init", "--goal", "Goal")

    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["history"] == [] and saved["current"] is None
    assert saved["next"] == [] and saved["recommended"] is None
    assert saved["completed"] is False
    assert saved["token_usage"]["total"] == 0
    assert result.stdout == ""
    assert not log.exists()


def test_session_bootstraps_persisted_unstarted_workflow(cli):
    run, step, log = cli
    assert run("init", "--goal", "Goal").returncode == 0

    result = run("session", input="break\n", replies=scenario("fresh"))

    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["current"] is None
    assert saved["next"][0]["slug"] == "first"
    assert saved["recommended"] == "first"
    assert [call["role"] for call in calls(log)] == ["coordinator"]
    assert result.stdout.endswith("break\n\n---\n")


def test_gate_does_not_accept_a_response_until_initial_bootstrap_is_rendered(
    cli,
):
    run, step, log = cli
    assert run("init", "--goal", "Goal").returncode == 0

    result = run("gate", "approved", replies=scenario("fresh"))

    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["current"] is None
    assert saved["next"][0]["slug"] == "first"
    assert saved["recommended"] == "first"
    assert [call["role"] for call in calls(log)] == ["coordinator"]
    assert result.stdout.startswith("# STEP Review - Initial Plan\n")


def test_gate_persists_bootstrap_usage_and_logs_it_before_review(cli):
    run, step, log = cli
    result = run("init", "--goal", "Goal")
    assert result.returncode == 0, result.stderr
    result = run("--log-level", "INFO", "gate", replies=scenario("fresh"))

    assert result.returncode == 0, result.stderr
    assert state(step)["token_usage"] == {
        "input": 100,
        "output": 50,
        "cache_read": 25,
        "cache_write": 0,
        "total": 175,
        "cost": 0.001,
    }
    assert result.stderr.index(
        "pi usage role=coordinator"
    ) < result.stderr.index("STEP token usage")
    assert [call["role"] for call in calls(log)] == ["coordinator"]


def test_missing_context_usage_does_not_block_bootstrap(cli):
    run, step, _ = cli
    replies = scenario("fresh")
    replies["session_stats"] = {
        "coordinator": {
            "tokens": {
                "input": 4,
                "output": 3,
                "cacheRead": 2,
                "cacheWrite": 1,
                "total": 10,
            },
            "cost": 0.01,
            "contextUsage": None,
        }
    }

    result = run("init", "--goal", "Goal")
    assert result.returncode == 0, result.stderr
    result = run("gate", replies=replies)

    assert result.returncode == 0, result.stderr
    assert state(step)["token_usage"]["total"] == 10
    assert state(step)["token_usage"]["cost"] == 0.01


def test_init_persists_selected_packet_history(cli):
    run, step, _ = cli
    result = run(
        "init",
        "--goal",
        "Goal",
        "--packet_history",
        "2",
        replies=scenario("fresh"),
    )

    assert result.returncode == 0, result.stderr
    assert state(step)["packet_history"] == 2


def test_init_rejects_empty_role_model_before_pi_invocation(cli):
    run, step, log = cli
    result = run(
        "init",
        "--goal",
        "Goal",
        "--coordinator-model",
        " ",
        replies=scenario("fresh"),
    )

    assert result.returncode == 2
    assert (
        "role_settings.coordinator.model must be a non-empty string"
        in result.stderr
    )
    assert not step.exists()
    assert not log.exists()


def test_role_settings_are_persisted_used_once_logged_and_not_repeated(cli):
    run, step, log = cli
    result = run(
        "--log-level",
        "INFO",
        "init",
        "--goal",
        "Goal",
        "--coordinator-model",
        "coordinator-model",
        "--worker-model",
        "worker-model",
        "--worker-thinking",
        "high",
        "--validator-model",
        "validator-model",
        "--validator-thinking",
        "low",
        "--assessor-model",
        "assessor-model",
        "--assessor-thinking",
        "xhigh",
    )

    assert result.returncode == 0, result.stderr
    assert result.stderr.count("role settings initialized") == 1
    assert state(step)["role_settings"] == {
        "coordinator": {"model": "coordinator-model", "thinking": "medium"},
        "worker": {"model": "worker-model", "thinking": "high"},
        "validator": {"model": "validator-model", "thinking": "low"},
        "assessor": {"model": "assessor-model", "thinking": "xhigh"},
    }

    result = run("gate", replies=scenario("fresh"))
    assert result.returncode == 0, result.stderr
    result = run(
        "--log-level",
        "INFO",
        "gate",
        "approved",
        replies=scenario("complete_continue"),
    )

    assert result.returncode == 0, result.stderr
    assert "role settings initialized" not in result.stderr
    settings = state(step)["role_settings"]
    for call in calls(log):
        role = call["role"]
        argv = call["argv"]
        assert argv[argv.index("--model") + 1] == settings[role]["model"]
        assert argv[argv.index("--thinking") + 1] == settings[role]["thinking"]


def test_pi_rpc_rejection_preserves_unstarted_step(cli):
    run, step, _ = cli
    result = run("init", "--goal", "Goal")
    assert result.returncode == 0, result.stderr
    before = step.read_bytes()
    result = run(
        "gate",
        replies={"rpc_errors": {"coordinator": "Model not found: rejected"}},
    )

    assert result.returncode == 3
    assert "CRITICAL" in result.stderr
    assert "role=coordinator" in result.stderr
    assert "model=gpt-5.6-terra" in result.stderr
    assert "thinking=medium" in result.stderr
    assert "Model not found: rejected" in result.stderr
    assert step.read_bytes() == before


def test_pi_thinking_rejection_preserves_persisted_step(cli):
    run, step, _ = cli
    init(run)
    configured = state(step)
    configured["current"] = configured["next"].pop(0)
    configured["recommended"] = None
    configured["role_settings"]["worker"]["thinking"] = "high"
    step.write_text(yaml.safe_dump(configured, sort_keys=False))
    before = step.read_bytes()

    result = run(
        "gate",
        replies={"startup_errors": {"worker": "Thinking level rejected"}},
    )

    assert result.returncode == 3
    assert "CRITICAL" in result.stderr
    assert "role=worker" in result.stderr
    assert "model=gpt-5.6-luna" in result.stderr
    assert "thinking=high" in result.stderr
    assert "Thinking level rejected" in result.stderr
    assert step.read_bytes() == before


def test_init_rejects_non_positive_packet_history(cli):
    run, step, log = cli
    result = run("init", "--goal", "Goal", "--packet_history", "0")

    assert result.returncode == 2
    assert "packet_history must be a positive integer" in result.stderr
    assert not step.exists()
    assert not log.exists()


def test_init_preserves_supplied_lessons_when_bootstrap_omits_them(cli):
    run, step, _ = cli
    result = run(
        "init",
        "--goal",
        "Goal",
        "--lesson",
        "Plan before implementing",
    )
    assert result.returncode == 0, result.stderr
    result = run("gate", replies={"coordinator": [coordinator("first")]})

    assert result.returncode == 0, result.stderr
    assert state(step)["lessons"] == ["Plan before implementing"]


def test_default_harness_sessions_are_named_logged_and_keep_state_clean(cli):
    run, step, log = cli
    result = run("init", "--goal", "Goal")
    assert result.returncode == 0, result.stderr
    result = run("--log-level", "INFO", "gate", replies=scenario("fresh"))
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
        r"^stagger_step\.harness\._role_session:\d+ "
        r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\] INFO: "
        r"pi role session started",
        result.stderr,
        re.MULTILINE,
    )
    assert "session_name=STEP-qual-bootstrap-coordinator" in result.stderr
    assert "session_id=" in result.stderr
    assert "session" not in step.read_text()


def test_debug_logs_prompt_body_and_buffered_thinking(cli):
    run, _, log = cli
    replies = {
        "coordinator": [
            {
                **coordinator("first"),
                "_thinking": "Inspecting\nthe current state.",
            }
        ]
    }

    result = run("init", "--goal", "Goal")
    assert result.returncode == 0, result.stderr
    result = run("--log-level", "DEBUG", "gate", replies=replies)

    assert result.returncode == 0, result.stderr
    header = (
        r"^stagger_step\.[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_]"
        r"[A-Za-z0-9_]*:\d+ \[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\] "
        r"(DEBUG|INFO|WARNING|ERROR|CRITICAL): "
    )
    prompt = calls(log)[0]["prompt"]
    assert re.search(
        header
        + r"harness_prompt role=coordinator task=bootstrap "
        + r"session_name=\S+ session_id=\S+ request_id=\S+ attempt=1\n"
        + re.escape(prompt)
        + r"\n(?=stagger_step\.)",
        result.stderr,
        re.MULTILINE,
    )
    assert re.search(
        header
        + r"pi thinking end role=coordinator task=bootstrap "
        + r"content_index=0 output=Inspecting the current state\.$",
        result.stderr,
        re.MULTILINE,
    )
    assert "pi rpc stdout" not in result.stderr
    assert '"type": "thinking_delta"' not in result.stderr


def test_harness_session_off_uses_no_session(cli):
    run, _, log = cli
    result = run("--harness-session", "off", "init", "--goal", "Goal")
    assert result.returncode == 0, result.stderr
    result = run("--harness-session", "off", "gate", replies=scenario("fresh"))
    assert result.returncode == 0, result.stderr
    argv = json.loads(log.read_text().splitlines()[0])["argv"]
    assert "--no-session" in argv
    assert "--session-id" not in argv


@pytest.mark.parametrize(
    "response", ("", "    ", " #@%567!  ", "5%@!#%", "abc")
)
def test_gate_ignores_nonsensical_feedback(cli, response):
    run, step, _ = cli
    init(run)
    before = step.read_text()

    result = run("gate", response)

    assert result.returncode == 0, result.stderr
    assert step.read_text() == before
    assert result.stdout.startswith("# STEP Review - Initial Plan\n")
    assert result.stdout.endswith("**Response:**\n")


def test_gate_approval_promotes_recommended_step(cli):
    run, step, _ = cli
    init(run)
    result = run("gate", "approved", replies=scenario("complete_continue"))
    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["history"] == [] and saved["current"]["slug"] == "first"
    assert "validate" not in saved["current"]
    assert saved["next"] == [] and saved["recommended"] is None
    assert "**Result:** success" in result.stdout
    assert load_state(step) == saved


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
    assert "worker.work must be a mapping" in worker_calls[1]["prompt"]
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
    assert "validate" not in state(step)["current"]
    assert "**Result:** partial" in result.stdout


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
    result = run("init", "--goal", "Goal")
    assert result.returncode == 0, result.stderr
    result = run(
        "gate", replies={"coordinator": ["no_finalizer", coordinator("first")]}
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
    result = run(
        "gate", "approved", replies={"worker": ["close", "close", "close"]}
    )
    assert result.returncode == 3
    assert "RPC closed before settlement" in result.stderr
    assert len([call for call in calls(log) if call["role"] == "worker"]) == 3
    assert state(step)["current"] == {
        "slug": "first",
        "intent": "first",
        "criteria": ["done"],
    }


def test_wrong_finalizer_is_rejected_without_step_state_mutation(cli):
    run, step, log = cli
    init(run)
    result = run(
        "gate",
        "approved",
        replies={"worker": ["wrong_finalizer", "wrong_finalizer"]},
    )
    assert result.returncode == 3
    assert "without stagger_step_finalize_worker" in result.stderr
    assert len([call for call in calls(log) if call["role"] == "worker"]) == 2
    assert state(step)["current"] == {
        "slug": "first",
        "intent": "first",
        "criteria": ["done"],
    }


def test_idle_timeout_reuses_the_session_and_replays_task(
    tmp_path, monkeypatch, caplog
):
    scenario_path = tmp_path / "scenario.json"
    log_path = tmp_path / "pi.log"
    scenario_path.write_text(
        json.dumps({"worker": ["sleep", "sleep", "sleep"]})
    )
    monkeypatch.setenv("FAKE_PI_SCENARIO", str(scenario_path))
    monkeypatch.setenv("FAKE_PI_LOG", str(log_path))
    monkeypatch.setattr(
        "stagger_step.harness._IDLE_TIMEOUT_SCHEDULE", (0.05, 0.1, 0.2)
    )
    harness = PiRpcHarness(command=(str(FAKE),), session_enabled=True)

    caplog.set_level(logging.DEBUG, logger="stagger_step.harness")
    with pytest.raises(
        HarnessError,
        match="worker harness failure: RPC idle timed out before settlement",
    ):
        harness.invoke("worker", "test timeout")

    prompt_records = [
        record
        for record in caplog.records
        if record.getMessage().startswith("harness_prompt ")
    ]
    assert len(prompt_records) == 3
    assert [record.body for record in prompt_records] == ["test timeout"] * 3
    assert [
        f"attempt={attempt}" in record.getMessage()
        for attempt, record in enumerate(prompt_records, 1)
    ] == [True] * 3

    attempts = calls(log_path)
    assert [attempt["prompt"] for attempt in attempts] == [
        "test timeout",
        "test timeout",
        "test timeout",
    ]
    session_ids = [
        attempt["argv"][attempt["argv"].index("--session-id") + 1]
        for attempt in attempts
    ]
    assert len(set(session_ids)) == 1


def test_activity_resets_the_rpc_idle_timeout(tmp_path, monkeypatch):
    scenario_path = tmp_path / "scenario.json"
    log_path = tmp_path / "pi.log"
    scenario_path.write_text(json.dumps({"worker": ["heartbeat"]}))
    monkeypatch.setenv("FAKE_PI_SCENARIO", str(scenario_path))
    monkeypatch.setenv("FAKE_PI_LOG", str(log_path))
    monkeypatch.setattr(
        "stagger_step.harness._IDLE_TIMEOUT_SCHEDULE", (0.15, 0.2, 0.3)
    )
    harness = PiRpcHarness(
        command=(str(FAKE),),
        max_invocation_seconds=1,
        session_enabled=False,
    )

    with pytest.raises(HarnessError, match="RPC closed before settlement"):
        harness.invoke("worker", "test activity")


def test_second_missing_finalizer_keeps_step_state_unchanged(cli):
    run, step, log = cli
    init(run)
    result = run(
        "--log-level",
        "DEBUG",
        "gate",
        "approved",
        replies={"worker": ["no_finalizer", "no_finalizer"]},
    )
    assert result.returncode == 3
    assert "without stagger_step_finalize_worker" in result.stderr
    worker_prompts = [
        call["prompt"] for call in calls(log) if call["role"] == "worker"
    ]
    assert len(worker_prompts) == 2
    assert worker_prompts[1].startswith("Finalize the current STEP role result")
    for prompt in worker_prompts:
        assert prompt in result.stderr
    assert result.stderr.count("DEBUG: harness_prompt role=worker") == 2
    assert state(step)["current"] == {
        "slug": "first",
        "intent": "first",
        "criteria": ["done"],
    }


def test_second_invalid_worker_packet_keeps_step_state_unchanged(cli):
    run, step, _ = cli
    init(run)
    invalid = {
        "packet": {"slug": "first", "intent": "first", "criteria": ["done"]}
    }
    result = run(
        "gate", "approved", replies={"worker": [invalid, {"packet": "invalid"}]}
    )
    assert result.returncode == 2
    assert "worker.work must be a mapping" in result.stderr
    assert state(step)["current"] == {
        "slug": "first",
        "intent": "first",
        "criteria": ["done"],
    }


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
    assert saved["next"] == []
    assert "### first-1" in result.stdout


def test_gate_approval_prepares_the_promoted_step_before_exit(cli):
    run, step, _ = cli
    init(
        run,
        {
            "coordinator": [
                {
                    "lessons": [],
                    "proposals": [
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
    assert "validate" not in saved["current"]
    assert saved["next"][0]["slug"] == "second"
    assert saved["recommended"] is None
    assert "**Result:** success" in result.stdout


def test_gate_prepares_cycle_before_rendering_and_final_signoff(cli):
    run, step, _ = cli
    init(run)
    rendered = run("gate", "approved", replies=scenario("terminal"))
    assert rendered.returncode == 0, rendered.stderr
    saved = state(step)
    assert saved["current"]["slug"] == "first"
    assert "validate" not in saved["current"]
    assert saved["next"] == [] and saved["recommended"] is None
    assert "**Result:** success" in rendered.stdout
    signed = run("gate", "approved", replies=scenario("terminal"))
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
        replies={
            "worker": [{"packet": complete("first")}],
            "assessor": [assessor("first")],
            "coordinator": [
                coordinator("second"),
                coordinator("third", ["revised lesson"]),
            ],
        },
    )
    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved == before
    assert "### third" in result.stdout
    assert "revised lesson" in result.stdout


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
                "proposals": [],
                "recommendation": "terminate",
            },
        ],
        "worker": [
            {
                "packet": {
                    "slug": "first",
                    "intent": "first",
                    "criteria": ["done"],
                    "work": {"summary": "worked", "evidence": ["file"]},
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
                    "work": {"summary": "worked", "evidence": ["file"]},
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
    assert result.stdout.count("**RECOMMENDED**") == 1
    assert result.stdout.count("**Response:**") == 2
    assert result.stdout.count("approved\n\n---\n") == 2
    assert result.stderr == ""


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
                    "work": {"summary": "worked", "evidence": ["file"]},
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
                    "work": {"summary": "worked", "evidence": ["file"]},
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
    assert saved["next"] == [] and saved["recommended"] is None
    assert "### third" in result.stdout
    assert result.stdout.endswith("break\n\n---\n")
    assert "STEP response:" not in result.stderr


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
    )
    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["change_path"] == "artifacts"
    assert saved["commit_mode"] is False

    result = run("gate", replies=scenario("fresh"))
    assert result.returncode == 0, result.stderr
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
