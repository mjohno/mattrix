from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from stagger_step.git import CommitMode
from stagger_step.state import StateError


def git(path: Path, *args: str) -> str:
    return subprocess.run(
        ("git", *args), cwd=path, text=True, capture_output=True, check=True
    ).stdout.strip()


def repository(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "project"
    root.mkdir()
    git(root, "init")
    git(root, "config", "user.name", "STEP Test")
    git(root, "config", "user.email", "step@example.test")
    (root / "tracked.txt").write_text("base\n")
    git(root, "add", "tracked.txt")
    git(root, "commit", "-m", "initial")
    step = root / "STEP-test.yaml"
    step.write_text("version: 1\n")
    return root, step


def packet() -> dict[str, object]:
    return {
        "slug": "update-file",
        "intent": "Update the tracked file\nwith a wrapped intent",
        "criteria": ["tracked file is updated"],
        "do": {"summary": "Changed tracked.txt", "evidence": []},
        "validate": {"result": "partial", "evidence": []},
    }


def test_commit_mode_commits_packet_changes_and_ignores_step_file(tmp_path):
    root, step = repository(tmp_path)
    mode = CommitMode(step, root)

    base = mode.begin()
    (root / "tracked.txt").write_text("changed\n")
    sha = mode.commit(packet(), base)

    assert sha == git(root, "rev-parse", "HEAD")
    assert git(root, "log", "-1", "--pretty=%B") == (
        "step(update-file): Update the tracked file with a wrapped intent\n\n"
        "Changed tracked.txt\n\nResult: partial"
    )
    assert git(root, "status", "--porcelain") == "?? STEP-test.yaml"


def test_commit_mode_skips_empty_packet_change_set(tmp_path):
    root, step = repository(tmp_path)
    mode = CommitMode(step, root)

    assert mode.commit(packet(), mode.begin()) is None
    assert git(root, "log", "-1", "--pretty=%s") == "initial"


def test_cli_approval_commits_before_persisting_history(tmp_path):
    root, step = repository(tmp_path)
    base = git(root, "rev-parse", "HEAD")
    (root / "tracked.txt").write_text("changed\n")
    step.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "goal": "Commit the packet",
                "lessons": [],
                "history": [],
                "current": {
                    **packet(),
                    "commit_base": base,
                },
                "next": [],
                "recommended": None,
                "completed": False,
            },
            sort_keys=False,
        )
    )
    package = Path(__file__).parents[2] / "src"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "stagger_step.cli",
            "--file",
            str(step),
            "--commit",
            "gate",
            "approved",
        ],
        cwd=root,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONPATH": str(package)},
        check=False,
    )

    assert result.returncode == 0, result.stderr
    saved = yaml.safe_load(step.read_text())
    assert saved["history"][0]["commit"] == git(root, "rev-parse", "HEAD")
    assert "commit_base" not in saved["history"][0]


def test_commit_mode_rejects_dirty_baseline(tmp_path):
    root, step = repository(tmp_path)
    (root / "unrelated.txt").write_text("do not commit\n")

    with pytest.raises(StateError, match="clean Git baseline: unrelated.txt"):
        CommitMode(step, root).begin()
