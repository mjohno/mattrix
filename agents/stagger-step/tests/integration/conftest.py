from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parents[2]
FAKE = Path(__file__).parent / "support/fake_pi.py"
SCENARIOS = ROOT / "tests/fixtures/scenarios.json"


def scenario(name: str) -> dict:
    return json.loads(SCENARIOS.read_text())[name]


@pytest.fixture
def cli(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "pi"
    fake.symlink_to(FAKE)
    fake.chmod(0o755)
    scenario, log, step = (
        tmp_path / "scenario.json",
        tmp_path / "pi.log",
        tmp_path / "STEP-qual.yaml",
    )

    def run(
        *args: str, input: str = "", replies: dict | None = None
    ) -> subprocess.CompletedProcess[str]:
        if replies is not None:
            scenario.write_text(json.dumps(replies))
            log.unlink(missing_ok=True)
        env = {
            **os.environ,
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "PYTHONPATH": str(ROOT / "src"),
            "STEP_FILE": str(step),
            "FAKE_PI_SCENARIO": str(scenario),
            "FAKE_PI_LOG": str(log),
        }
        env.pop("STAGGER_STEP_HARNESS_SESSION", None)
        return subprocess.run(
            [sys.executable, "-m", "stagger_step.cli", *args],
            cwd=ROOT,
            input=input,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    return run, step, log


def state(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def gate(stdout: str) -> dict:
    return yaml.safe_load(stdout.split("STEP response:", 1)[0])


def calls(log: Path) -> list[dict]:
    return (
        [json.loads(line) for line in log.read_text().splitlines()]
        if log.exists()
        else []
    )


def task(slug: str) -> dict:
    return {"slug": slug, "intent": slug.replace("-", " "), "criteria": ["done"]}


def complete(slug: str) -> dict:
    return {
        **task(slug),
        "do": {"summary": "worked", "evidence": ["file"]},
        "validate": {"result": "success", "evidence": ["test"]},
    }


def coordinator(slug: str | None, lessons: list[str] | None = None) -> dict:
    return {
        "lessons": lessons or [],
        "proposed_next_packets": [] if slug is None else [task(slug)],
        "recommendation": slug,
    }


def assessor(slug: str, clarify: bool = False) -> dict:
    return {
        "current_packet": complete(slug),
        "retro": {"wins": ["progress"], "issues": [], "actions": ["continue"]},
        "clarification_needed": clarify,
    }
