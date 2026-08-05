from __future__ import annotations

import subprocess

import pytest

from .conftest import assessor, complete, coordinator, state

pytestmark = pytest.mark.integration


def git(path, *args: str) -> str:
    return subprocess.run(
        ("git", *args), cwd=path, text=True, capture_output=True, check=True
    ).stdout.strip()


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
        "--commit",
        "init",
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
    assert git(repository, "log", "-1", "--pretty=%s") == "step(first): first"
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
        "--commit",
        "init",
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
