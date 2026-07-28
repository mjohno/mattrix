from __future__ import annotations
import pytest
from .conftest import assessor, calls, complete, coordinator, gate, scenario, state, task

pytestmark = pytest.mark.integration

def init(run):
    result = run("init", "--goal", "Goal")
    assert result.returncode == 0, result.stderr

def test_fresh_approval_promotes_recommended_task(cli):
    run, step, log = cli; init(run)
    result = run("session", input="approved\n", replies=scenario("fresh"))
    assert result.returncode == 0, result.stderr
    displayed = gate(result.stdout)
    assert displayed["current_packet"] is None and displayed["recommendation"] == "first" and displayed["lessons"] == ["coordinator lesson"]
    saved = state(step)
    assert saved["active_packet"]["slug"] == "first" and saved["lessons"] == ["coordinator lesson"] and saved["history"] == []
    assert [entry["role"] for entry in calls(log)] == ["coordinator"]
    assert calls(log)[0]["step_file"] is None

def test_complete_continue_is_user_visible_serial_flow(cli):
    run, step, log = cli; init(run)
    run("session", input="approved\n", replies={"coordinator": [coordinator("first")]})
    result = run("session", input="approved\n", replies=scenario("complete_continue"))
    assert result.returncode == 0, result.stderr
    displayed = gate(result.stdout)
    assert displayed["current_packet"]["slug"] == "first" and displayed["recommendation"] == "second" and displayed["lessons"] == ["chosen by coordinator"]
    saved = state(step)
    assert saved["history"][0]["slug"] == "first" and saved["active_packet"]["slug"] == "second" and saved["lessons"] == ["chosen by coordinator"]
    records = calls(log)
    assert [entry["role"] for entry in records] == ["worker", "assessor", "coordinator"]
    assert all(entry["step_file"] is None for entry in records)
    assert "worker_packet:" not in records[0]["prompt"] and "history:" not in records[1]["prompt"] and "worker_packet:" not in records[2]["prompt"]

def test_terminal_approval_commits_completion(cli):
    run, step, _ = cli; init(run)
    run("session", input="approved\n", replies={"coordinator": [coordinator("first")]})
    result = run("session", input="approved\n", replies=scenario("terminal"))
    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["completed"] is True and saved["active_packet"] is None and saved["history"][0]["slug"] == "first"

def test_break_and_revision_never_write_pending_state(cli):
    run, step, log = cli; init(run)
    run("session", input="approved\n", replies={"coordinator": [coordinator("first")]})
    before = step.read_bytes()
    paused = run("session", input="break\n", replies=scenario("terminal"))
    assert paused.returncode == 0 and step.read_bytes() == before
    revised = run("session", input="use another task\nbreak\n", replies={"worker": [{"packet": complete("first")}], "assessor": [assessor("first")], "coordinator": [coordinator("second"), coordinator("third", ["revised lesson"])]})
    assert revised.returncode == 0 and step.read_bytes() == before

def test_malformed_role_output_does_not_write(cli):
    run, step, _ = cli; init(run)
    run("session", input="approved\n", replies={"coordinator": [coordinator("first")]})
    before = step.read_bytes()
    result = run("session", replies=scenario("malformed_worker"))
    assert result.returncode == 3 and step.read_bytes() == before

def test_manual_state_and_one_clarification_round(cli):
    run, step, log = cli; init(run)
    run("session", input="approved\n", replies={"coordinator": [coordinator("first")]})
    result = run("session", input="approved\n", replies={"worker": [{"packet": complete("first")}, {"packet": complete("first")}], "assessor": [assessor("first", True), assessor("first", False)], "coordinator": [coordinator(None)]})
    assert result.returncode == 0
    assert [entry["role"] for entry in calls(log)] == ["worker", "assessor", "worker", "assessor", "coordinator"]
    saved = state(step); saved["lessons"] = ["manual valid edit"]
    step.write_text(__import__("yaml").safe_dump(saved))
    assert run("validate").returncode == 0
    saved["completed"] = False
    step.write_text(__import__("yaml").safe_dump(saved))
    assert run("validate").returncode == 2
