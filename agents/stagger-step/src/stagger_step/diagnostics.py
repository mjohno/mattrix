from __future__ import annotations

import os
import sys
import tempfile
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

_REDACTED = "[redacted]"
_SECRET_MARKERS = ("secret", "password", "token", "api_key", "apikey", "authorization")


def artifact_paths(step_file: Path) -> tuple[Path, Path]:
    stem = step_file.stem
    slug = stem.removeprefix("STEP-") or stem
    return (
        step_file.with_name(f"STEPTRACE-{slug}.yaml"),
        step_file.with_name(f"STEPDUMP-{slug}.yaml"),
    )


def _redact(value: Any, key: str = "") -> Any:
    if any(marker in key.lower() for marker in _SECRET_MARKERS):
        return _REDACTED
    if isinstance(value, dict):
        return {str(k): _redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def _write_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as stream:
        yaml.safe_dump(_redact(value), stream, sort_keys=False)
        temporary = Path(stream.name)
    os.replace(temporary, path)


def write_diagnostics(
    step_file: Path | None, *, event: str, error: BaseException | None = None
) -> tuple[Path, Path] | None:
    """Write the latest human-readable failure evidence on a best-effort basis."""
    if step_file is None:
        return None
    trace_path, dump_path = artifact_paths(step_file)
    now = datetime.now(UTC).isoformat()
    trace: dict[str, Any] = {
        "event": event,
        "at": now,
        "command": sys.argv,
        "step_file": str(step_file),
    }
    if error is not None:
        trace["error"] = {"type": type(error).__name__, "message": str(error)}
    dump: dict[str, Any] = {"event": event, "at": now, "step_file": str(step_file)}
    if step_file.exists():
        try:
            dump["state"] = yaml.safe_load(step_file.read_text())
        except Exception as exc:  # Diagnostics must still explain unreadable state.
            dump["state_read_error"] = f"{type(exc).__name__}: {exc}"
    if error is not None:
        dump["exception"] = "".join(traceback.format_exception(error))
    try:
        _write_atomic(trace_path, trace)
        _write_atomic(dump_path, dump)
    except Exception:
        return None
    return trace_path, dump_path
