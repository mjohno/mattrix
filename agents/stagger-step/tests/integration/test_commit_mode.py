from __future__ import annotations

import subprocess

import pytest
import yaml
from stagger_step.state import default_role_settings, default_token_usage

from .conftest import assessor, calls, complete, coordinator, state

pytestmark = pytest.mark.integration


def git(path, *args: str) -> str:
    return subprocess.run(
        ("git", *args), cwd=path, text=True, capture_output=True, check=True
    ).stdout.strip()


def test_init_combines_relative_change_path_and_persisted_commit_mode(
    git_cli,
):
    run, step, log, _ = git_cli
    artifacts = step.parent / "artifacts"
    artifacts.mkdir()

    result = run(
        "init",
        "--goal",
        "Goal",
        "--change",
        "artifacts",
        "--commit",
        replies={"coordinator": [coordinator("first")]},
    )

    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["change_path"] == "artifacts"
    assert saved["commit_mode"] is True
    assert f"`{artifacts.resolve()}`" in calls(log)[0]["prompt"]


def test_commit_session_commits_approved_worker_changes_and_records_sha(
    git_cli,
):
    run, step, _, repository = git_cli
    packet = complete("first")
    replies = {
        "coordinator": [coordinator("first"), coordinator(None)],
        "worker": [
            {
                "_write": {"tracked.txt": "changed\n"},
                "packet": packet,
            }
        ],
        "assessor": [assessor("first")],
    }

    result = run(
        "init",
        "--commit",
        "--goal",
        "Goal",
        "--session",
        input="approved\napproved\n",
        replies=replies,
    )

    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["completed"] is True
    assert saved["history"][0]["commit"] == git(repository, "rev-parse", "HEAD")
    assert git(repository, "log", "-1", "--pretty=%s") == "step: first"
    assert git(repository, "status", "--porcelain") == ""


def test_commit_session_advances_a_noop_packet_without_a_commit(git_cli):
    run, step, _, repository = git_cli
    initial = git(repository, "rev-parse", "HEAD")
    replies = {
        "coordinator": [coordinator("first"), coordinator(None)],
        "worker": [{"packet": complete("first")}],
        "assessor": [assessor("first")],
    }

    result = run(
        "init",
        "--commit",
        "--goal",
        "Goal",
        "--session",
        input="approved\napproved\n",
        replies=replies,
    )

    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["completed"] is True
    assert "commit" not in saved["history"][0]
    assert git(repository, "rev-parse", "HEAD") == initial


def test_commit_off_bypasses_persisted_commit_mode_without_state_mutation(
    git_cli,
):
    run, step, _, repository = git_cli
    result = run(
        "init",
        "--goal",
        "Goal",
        "--commit",
        replies={"coordinator": [coordinator("first")]},
    )
    assert result.returncode == 0, result.stderr
    initial = git(repository, "rev-parse", "HEAD")
    (repository / "unrelated.txt").write_text("dirty\n")

    result = run(
        "gate",
        "approved",
        "--commit-off",
        replies={
            "worker": [
                {
                    "_write": {"tracked.txt": "changed\n"},
                    "packet": complete("first"),
                }
            ],
            "assessor": [assessor("first")],
            "coordinator": [coordinator("second")],
        },
    )

    assert result.returncode == 0, result.stderr
    saved = state(step)
    assert saved["commit_mode"] is True
    assert "commit_base" not in saved["current"]
    assert git(repository, "rev-parse", "HEAD") == initial


def test_session_commit_off_preserves_existing_packet_commit_state(git_cli):
    run, step, _, repository = git_cli
    base = git(repository, "rev-parse", "HEAD")
    configured = {
        "version": 1,
        "goal": "Goal",
        "role_settings": default_role_settings(),
        "token_usage": default_token_usage(),
        "change_path": None,
        "commit_mode": True,
        "packet_history": 5,
        "lessons": [],
        "history": [],
        "current": {**complete("first"), "commit_base": base},
        "next": [],
        "recommended": "terminate",
        "completed": False,
    }
    step.write_text(yaml.safe_dump(configured, sort_keys=False))
    before = step.read_bytes()
    (repository / "unrelated.txt").write_text("dirty\n")

    result = run("session", "--commit-off", input="break\n")

    assert result.returncode == 0, result.stderr
    assert step.read_bytes() == before
    assert git(repository, "rev-parse", "HEAD") == base
