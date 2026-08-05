from __future__ import annotations

import yaml
from stagger_step.diagnostics import artifact_path, write_diagnostics


def test_writes_one_redacted_debug_artifact_and_removes_legacy_files(tmp_path):
    step_file = tmp_path / "STEP-eval.yaml"
    step_file.write_text("token: secret-value\ngoal: Evaluate\n")
    trace = tmp_path / "STEPTRACE-eval.yaml"
    dump = tmp_path / "STEPDUMP-eval.yaml"
    trace.write_text("old trace")
    dump.write_text("old dump")

    try:
        raise RuntimeError("failed")
    except RuntimeError as error:
        result = write_diagnostics(
            step_file, event="unhandled_failure", error=error
        )

    assert result == artifact_path(step_file)
    debug = yaml.safe_load(result.read_text())
    assert debug["event"] == "unhandled_failure"
    assert debug["error"] == {"type": "RuntimeError", "message": "failed"}
    assert "RuntimeError: failed" in debug["traceback"]
    assert debug["state"]["token"] == "[redacted]"
    assert debug["state"]["goal"] == "Evaluate"
    assert not trace.exists()
    assert not dump.exists()


def test_returns_none_without_a_step_file():
    assert write_diagnostics(None, event="SIGINT") is None
