from __future__ import annotations

import json
import logging
import os
import re
import select
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path
from typing import Any, Protocol

from .state import StateError


class HarnessError(RuntimeError):
    pass


class PacketNormalizationError(StateError):
    pass


class FinalizerProtocolError(HarnessError):
    pass


logger = logging.getLogger("stagger_step.harness")


def _default_pi_command() -> tuple[str, ...]:
    executable = "pi.cmd" if os.name == "nt" else "pi"
    return (executable, "--mode", "rpc", "--no-session")


class Harness(Protocol):
    def begin_transition(self) -> None: ...
    def invoke(
        self,
        role: str,
        prompt: str,
        *,
        task_slug: str = "bootstrap",
        follow_up: bool = False,
    ) -> dict[str, Any]: ...
    def close(self) -> None: ...


@dataclass(frozen=True)
class RoleSession:
    session_id: str
    name: str


@dataclass
class PiRpcHarness:
    """Run one short-lived Pi RPC process per role without exposing STEP files."""

    command: tuple[str, ...] = field(default_factory=_default_pi_command)
    timeout_seconds: float = 120.0
    retries: int = 2
    session_enabled: bool = True
    session_scope: str = "STEP-default.yaml"
    normalizer_command: tuple[str, ...] = (
        sys.executable,
        "-m",
        "stagger_step.cli",
    )
    _role_sessions: dict[str, RoleSession] = field(
        default_factory=dict, init=False
    )

    def __post_init__(self) -> None:
        self._step_slug()

    def begin_transition(self) -> None:
        """Forget Pi conversations before beginning a new STEP transition."""
        self._role_sessions.clear()

    def _step_slug(self) -> str:
        stem = os.path.splitext(os.path.basename(self.session_scope))[0]
        slug = stem.removeprefix("STEP-")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise HarnessError(
                "STEP file basename must be lowercase kebab-case for Pi naming"
            )
        return slug

    def _session_name(self, role: str, task_slug: str = "bootstrap") -> str:
        if role not in {"coordinator", "worker", "assessor"}:
            raise HarnessError(f"unknown STEP role: {role}")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", task_slug):
            raise HarnessError(
                "task slug must be lowercase kebab-case for Pi naming"
            )
        return f"STEP-{self._step_slug()}-{task_slug}-{role}"

    def _role_session(self, role: str, task_slug: str) -> RoleSession:
        session = self._role_sessions.get(role)
        if session is not None:
            return session
        session = RoleSession(
            str(uuid.uuid4()), self._session_name(role, task_slug)
        )
        self._role_sessions[role] = session
        logger.info(
            "pi role session started role=%s session_name=%s session_id=%s persistent=%s",
            role,
            session.name,
            session.session_id,
            self.session_enabled,
        )
        return session

    def _session_id(self, role: str, task_slug: str = "bootstrap") -> str:
        return self._role_session(role, task_slug).session_id

    def invoke(
        self,
        role: str,
        prompt: str,
        *,
        task_slug: str = "bootstrap",
        follow_up: bool = False,
    ) -> dict[str, Any]:
        # A role reconnects only within the active transition for retry,
        # correction, or clarification follow-ups.
        del follow_up
        session = self._role_session(role, task_slug)
        repair_prompt: str | None = None
        for attempt in range(self.retries + 1):
            try:
                return self._invoke_once(role, repair_prompt or prompt, session)
            except (PacketNormalizationError, FinalizerProtocolError) as exc:
                if repair_prompt is not None:
                    raise
                repair_prompt = (
                    f"{prompt}\n\nYour previous {role} response was invalid: {exc}. "
                    f"Do not return YAML directly. Call "
                    f"stagger_step_finalize_{role} exactly once with one complete "
                    "conforming YAML packet."
                )
            except (OSError, HarnessError) as exc:
                if attempt == self.retries:
                    raise HarnessError(
                        f"{role} harness failure: {exc}"
                    ) from exc
                logger.error(
                    "pi invocation retry role=%s attempt=%s error=%s",
                    role,
                    attempt + 1,
                    exc,
                )
                time.sleep(0.1 * (2**attempt))
        raise AssertionError("unreachable")

    @staticmethod
    def _extension_path() -> Path:
        return Path(
            str(files("stagger_step").joinpath("pi_extension", "index.ts"))
        )

    @staticmethod
    def _read_stdout_line(stream: Any, timeout: float) -> str:
        if os.name == "nt":
            # Windows select() supports sockets only, not subprocess pipes. This
            # blocking read intentionally has no per-read timeout; Ctrl+C remains
            # available while a nonresponsive Pi/Llama process is awaited.
            return stream.readline()
        readable, _, _ = select.select([stream], [], [], timeout)
        if not readable:
            raise HarnessError("RPC timed out before settlement")
        return stream.readline()

    def _normalize(self, role: str, text: str) -> dict[str, Any]:
        result = subprocess.run(
            [*self.normalizer_command, "normalize", "--role", role],
            input=text,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            error = result.stderr.strip() or "normalization failed"
            raise PacketNormalizationError(
                f"{role} finalizer rejected packet: {error}"
            )
        return _yaml_mapping(result.stdout)

    def _invoke_once(
        self, role: str, prompt: str, session: RoleSession
    ) -> dict[str, Any]:
        command = [
            *self.command,
            "--extension",
            str(self._extension_path()),
            "--step-role",
            role,
        ]
        session_id = session.session_id
        if self.session_enabled:
            command = [part for part in command if part != "--no-session"]
            command.extend(("--session-id", session_id))
        env = {
            key: value
            for key, value in os.environ.items()
            if key != "STEP_FILE" and not key.startswith("STAGGER_STEP_")
        }
        proc = subprocess.Popen(
            [*command, "--name", session.name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        logger.info(
            "pi spawn role=%s session_id=%s persistent=%s pid=%s",
            role,
            session_id,
            self.session_enabled,
            proc.pid,
        )
        request = {"id": str(uuid.uuid4()), "type": "prompt", "message": prompt}
        logger.debug(
            "pi rpc request session_id=%s payload=%s",
            session_id,
            json.dumps(request),
        )
        try:
            assert proc.stdin and proc.stdout
            proc.stdin.write(json.dumps(request) + "\n")
            proc.stdin.flush()
            deadline, finalizer_text, finalizer_error, settled = (
                time.monotonic() + self.timeout_seconds,
                None,
                None,
                False,
            )
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise HarnessError("RPC timed out before settlement")
                line = self._read_stdout_line(proc.stdout, remaining)
                if not line:
                    raise HarnessError("RPC closed before settlement")
                logger.debug(
                    "pi rpc stdout session_id=%s payload=%s",
                    session_id,
                    line.rstrip(),
                )
                event = json.loads(line)
                if event.get("type") == "agent_settled":
                    settled = True
                    break
                if (
                    event.get("type") == "response"
                    and event.get("success") is False
                ):
                    raise HarnessError(
                        event.get("error", "RPC rejected request")
                    )
                if (
                    event.get("type") == "tool_execution_end"
                    and event.get("toolName") == f"stagger_step_finalize_{role}"
                ):
                    result = event.get("result")
                    if not isinstance(result, dict):
                        finalizer_error = "finalizer returned no result"
                        continue
                    chunks = [
                        content.get("text", "")
                        for content in result.get("content", [])
                        if isinstance(content, dict)
                        and content.get("type") == "text"
                    ]
                    if result.get("isError"):
                        detail = "".join(chunks).strip()
                        finalizer_error = (
                            f"finalizer reported an error: {detail}"
                            if detail
                            else "finalizer reported an error"
                        )
                        continue
                    if not chunks:
                        finalizer_error = "finalizer returned no text"
                        continue
                    finalizer_text = "".join(chunks)
                    finalizer_error = None
            if not settled:
                raise HarnessError("RPC did not settle")
            if finalizer_error is not None:
                raise FinalizerProtocolError(finalizer_error)
            if finalizer_text is None:
                raise FinalizerProtocolError(
                    f"RPC settled without stagger_step_finalize_{role}"
                )
            payload = self._normalize(role, finalizer_text)
            logger.info("pi settled role=%s session_id=%s", role, session_id)
            return payload
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
            if proc.stderr:
                stderr = proc.stderr.read()
                if stderr:
                    logger.debug(
                        "pi stderr session_id=%s payload=%s",
                        session_id,
                        stderr.rstrip(),
                    )

    def close(self) -> None:
        pass


def _yaml_mapping(text: str) -> dict[str, Any]:
    try:
        import yaml

        value = yaml.safe_load(text)
    except Exception as exc:
        raise HarnessError(f"malformed role YAML: {exc}") from exc
    if not isinstance(value, dict):
        raise HarnessError("role output must be a YAML mapping")
    return value
