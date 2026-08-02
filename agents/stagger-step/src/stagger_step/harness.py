from __future__ import annotations

import json
import logging
import os
import queue
import re
import signal
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path
from typing import Any, Protocol

from .prompts import build_continuation_prompt, build_finalization_prompt
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
    max_invocation_seconds: float | None = 1800.0
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
        retry_prompt = prompt
        finalization_retried = False
        for attempt in range(self.retries + 1):
            try:
                return self._invoke_once(role, retry_prompt, session)
            except (PacketNormalizationError, FinalizerProtocolError) as exc:
                if finalization_retried:
                    raise
                # The role has completed its work but its result was not accepted.
                # Preserve the session and ask only for finalizer formatting.
                retry_prompt = build_finalization_prompt(role, exc)
                finalization_retried = True
            except (OSError, HarnessError) as exc:
                if attempt == self.retries:
                    raise HarnessError(
                        f"{role} harness failure: {exc}"
                    ) from exc
                if str(exc) == "RPC idle timed out before settlement":
                    retry_prompt = build_continuation_prompt(role)
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
    def _start_pipe_reader(stream: Any) -> queue.Queue[str | None]:
        lines: queue.Queue[str | None] = queue.Queue()

        def read_lines() -> None:
            try:
                for line in stream:
                    lines.put(line)
            finally:
                lines.put(None)

        threading.Thread(target=read_lines, daemon=True).start()
        return lines

    @staticmethod
    def _read_stdout_line(
        lines: queue.Queue[str | None], timeout: float, timeout_error: str
    ) -> str:
        try:
            line = lines.get(timeout=timeout)
        except queue.Empty as exc:
            raise HarnessError(timeout_error) from exc
        if line is None:
            raise HarnessError("RPC closed before settlement")
        return line

    @staticmethod
    def _drain_pipe(lines: queue.Queue[str | None]) -> str:
        chunks: list[str] = []
        while True:
            try:
                line = lines.get_nowait()
            except queue.Empty:
                return "".join(chunks)
            if line is not None:
                chunks.append(line)

    @staticmethod
    def _close_pipe(stream: Any) -> None:
        if stream is None:
            return
        try:
            stream.close()
        except OSError:
            pass

    def _kill_process_tree(self, proc: subprocess.Popen[str]) -> None:
        if os.name == "nt":
            # TODO: start Pi in a new Windows process group and send
            # CTRL_BREAK_EVENT before escalating to taskkill.
            try:
                result = subprocess.run(
                    ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                logger.error("pi process-tree kill timed out pid=%s", proc.pid)
            except OSError as exc:
                logger.error("pi process-tree kill failed pid=%s error=%s", proc.pid, exc)
            else:
                logger.debug(
                    "pi process-tree kill pid=%s returncode=%s stdout=%s stderr=%s",
                    proc.pid,
                    result.returncode,
                    result.stdout.rstrip(),
                    result.stderr.rstrip(),
                )
            return
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except OSError as exc:
            logger.error("pi process-group kill failed pid=%s error=%s", proc.pid, exc)

    def _terminate_process(
        self,
        proc: subprocess.Popen[str],
        session: RoleSession,
        stderr_lines: queue.Queue[str | None],
    ) -> None:
        logger.debug(
            "pi cleanup begin session_name=%s session_id=%s pid=%s",
            session.name,
            session.session_id,
            proc.pid,
        )
        self._close_pipe(proc.stdin)
        try:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=2)
                logger.debug("pi cleanup terminated pid=%s", proc.pid)
        except subprocess.TimeoutExpired:
            logger.warning("pi cleanup terminate timed out pid=%s", proc.pid)
            self._kill_process_tree(proc)
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                logger.error("pi cleanup kill timed out pid=%s", proc.pid)
        except ProcessLookupError:
            pass
        finally:
            self._close_pipe(proc.stdout)
            self._close_pipe(proc.stderr)
        stderr = self._drain_pipe(stderr_lines)
        if stderr:
            logger.debug(
                "pi stderr session_name=%s session_id=%s payload=%s",
                session.name,
                session.session_id,
                stderr.rstrip(),
            )
        logger.debug(
            "pi cleanup complete session_name=%s session_id=%s pid=%s",
            session.name,
            session.session_id,
            proc.pid,
        )

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
        popen_options: dict[str, Any] = {}
        if os.name != "nt":
            popen_options["start_new_session"] = True
        proc = subprocess.Popen(
            [*command, "--name", session.name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            **popen_options,
        )
        logger.info(
            "pi spawn role=%s session_name=%s session_id=%s persistent=%s pid=%s",
            role,
            session.name,
            session_id,
            self.session_enabled,
            proc.pid,
        )
        request = {"id": str(uuid.uuid4()), "type": "prompt", "message": prompt}
        logger.debug(
            "pi rpc request session_name=%s session_id=%s payload=%s",
            session.name,
            session_id,
            json.dumps(request),
        )
        stderr_lines: queue.Queue[str | None] = queue.Queue()
        try:
            assert proc.stdin and proc.stdout and proc.stderr
            stdout_lines = self._start_pipe_reader(proc.stdout)
            stderr_lines = self._start_pipe_reader(proc.stderr)
            proc.stdin.write(json.dumps(request) + "\n")
            proc.stdin.flush()
            started = last_activity = time.monotonic()
            maximum_deadline = (
                started + self.max_invocation_seconds
                if self.max_invocation_seconds is not None
                else None
            )
            finalizer_text, finalizer_error, settled = None, None, False
            while True:
                idle_remaining = self.timeout_seconds - (
                    time.monotonic() - last_activity
                )
                if idle_remaining <= 0:
                    raise HarnessError("RPC idle timed out before settlement")
                remaining = idle_remaining
                timeout_error = "RPC idle timed out before settlement"
                if maximum_deadline is not None:
                    maximum_remaining = maximum_deadline - time.monotonic()
                    if maximum_remaining <= 0:
                        raise HarnessError(
                            "RPC exceeded maximum duration before settlement"
                        )
                    if maximum_remaining < remaining:
                        remaining = maximum_remaining
                        timeout_error = (
                            "RPC exceeded maximum duration before settlement"
                        )
                line = self._read_stdout_line(
                    stdout_lines, remaining, timeout_error
                )
                last_activity = time.monotonic()
                logger.debug(
                    "pi rpc stdout session_name=%s session_id=%s payload=%s",
                    session.name,
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
            logger.info(
                "pi settled role=%s session_name=%s session_id=%s",
                role,
                session.name,
                session_id,
            )
            return payload
        finally:
            self._terminate_process(proc, session, stderr_lines)

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
