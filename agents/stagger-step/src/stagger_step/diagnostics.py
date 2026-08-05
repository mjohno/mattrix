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
_SECRET_MARKERS = (
    "secret",
    "password",
    "token",
    "api_key",
    "apikey",
    "authorization",
)


def artifact_path(step_file: Path) -> Path:
    stem = step_file.stem
    slug = stem.removeprefix("STEP-") or stem
    return step_file.with_name(f"STEPDEBUG-{slug}.yaml")


def _legacy_artifact_paths(step_file: Path) -> tuple[Path, Path]:
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
) -> Path | None:
    """Write one atomic, redacted failure artifact on a best-effort basis."""
    if step_file is None:
        return None
    debug_path = artifact_path(step_file)
    debug: dict[str, Any] = {
        "event": event,
        "at": datetime.now(UTC).isoformat(),
        "command": sys.argv,
        "step_file": str(step_file),
    }
    if error is not None:
        debug["error"] = {"type": type(error).__name__, "message": str(error)}
        debug["traceback"] = "".join(traceback.format_exception(error))
    if step_file.exists():
        try:
            debug["state"] = yaml.safe_load(step_file.read_text())
        except (
            Exception
        ) as exc:  # Diagnostics must still explain unreadable state.
            debug["state_read_error"] = f"{type(exc).__name__}: {exc}"
    try:
        _write_atomic(debug_path, debug)
        for legacy_path in _legacy_artifact_paths(step_file):
            legacy_path.unlink(missing_ok=True)
    except Exception:
        return None
    return debug_path
