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

from .prompts import build_finalization_prompt
from .state import StateError, default_role_settings


class HarnessError(RuntimeError):
    pass


class PiConfigurationError(HarnessError):
    pass


class PacketNormalizationError(StateError):
    pass


class FinalizerProtocolError(HarnessError):
    pass


logger = logging.getLogger("stagger_step.harness")
_IDLE_TIMEOUT_SCHEDULE = (30.0, 60.0, 120.0)
# Set a positive character limit here to truncate individual DEBUG values; None is unlimited.
_DEBUG_VALUE_LIMIT: int | None = None
_SENSITIVE_FIELD = re.compile(
    r"(?:api[-_]?key|authorization|cookie|password|secret|token)", re.I
)


def _inline_debug_text(value: object) -> str:
    """Keep one debug record readable and bounded."""
    text = " ".join(str(value).split())
    if _DEBUG_VALUE_LIMIT is not None and len(text) > _DEBUG_VALUE_LIMIT:
        return text[:_DEBUG_VALUE_LIMIT] + "…"
    return text


def _safe_debug_value(value: object) -> str:
    """Serialize tool data without leaking common credential fields."""

    def redact(item: object) -> object:
        if isinstance(item, dict):
            return {
                str(key): (
                    "[redacted]"
                    if _SENSITIVE_FIELD.search(str(key))
                    else redact(child)
                )
                for key, child in item.items()
            }
        if isinstance(item, list):
            return [redact(child) for child in item]
        return item

    rendered = json.dumps(
        redact(value), default=str, ensure_ascii=False, separators=(",", ":")
    )
    return _inline_debug_text(rendered)


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


@dataclass(frozen=True)
class RoleSession:
    session_id: str
    name: str


@dataclass
class PiRpcHarness:
    """Run one short-lived Pi RPC process per role without exposing STEP files."""

    command: tuple[str, ...] = field(default_factory=_default_pi_command)
    max_invocation_seconds: float | None = 1800.0
    session_enabled: bool = True
    session_scope: str = "STEP-default.yaml"
    normalizer_command: tuple[str, ...] = (
        sys.executable,
        "-m",
        "stagger_step.cli",
    )
    role_settings: dict[str, dict[str, str]] = field(
        default_factory=default_role_settings
    )
    _role_sessions: dict[str, RoleSession] = field(
        default_factory=dict, init=False
    )
    _last_finalizer_details: dict[str, Any] | None = field(
        default=None, init=False
    )
    _session_usage: dict[str, dict[str, float]] = field(
        default_factory=dict, init=False
    )
    _transition_usage: dict[str, float] = field(
        default_factory=lambda: {
            "input": 0,
            "output": 0,
            "cache_read": 0,
            "cache_write": 0,
            "total": 0,
            "cost": 0.0,
        },
        init=False,
    )

    @property
    def last_finalizer_details(self) -> dict[str, Any] | None:
        """Diagnostic details from the most recently accepted finalizer."""
        return self._last_finalizer_details

    def __post_init__(self) -> None:
        self._step_slug()

    def begin_transition(self) -> None:
        """Forget Pi conversations before beginning a new STEP transition."""
        self._role_sessions.clear()
        self._session_usage.clear()
        self._transition_usage = {
            "input": 0,
            "output": 0,
            "cache_read": 0,
            "cache_write": 0,
            "total": 0,
            "cost": 0.0,
        }

    def consume_transition_usage(self) -> dict[str, float]:
        """Return and clear newly collected usage for the active transition."""
        usage = self._transition_usage.copy()
        self._transition_usage = {
            "input": 0,
            "output": 0,
            "cache_read": 0,
            "cache_write": 0,
            "total": 0,
            "cost": 0.0,
        }
        return usage

    def _record_session_stats(
        self, role: str, task_slug: str, session: RoleSession, data: Any
    ) -> None:
        if not isinstance(data, dict) or not isinstance(
            data.get("tokens"), dict
        ):
            raise HarnessError("get_session_stats returned invalid token data")
        tokens = data["tokens"]
        values = {
            "input": tokens.get("input"),
            "output": tokens.get("output"),
            "cache_read": tokens.get("cacheRead"),
            "cache_write": tokens.get("cacheWrite"),
            "total": tokens.get("total"),
            "cost": data.get("cost"),
        }
        token_keys = ("input", "output", "cache_read", "cache_write", "total")
        if any(
            not isinstance(values[key], int)
            or isinstance(values[key], bool)
            or values[key] < 0
            for key in token_keys
        ) or (
            not isinstance(values["cost"], (int, float))
            or isinstance(values["cost"], bool)
            or values["cost"] < 0
        ):
            raise HarnessError(
                "get_session_stats returned invalid usage values"
            )
        if values["total"] != sum(values[key] for key in token_keys[:-1]):
            raise HarnessError(
                "get_session_stats total does not match token components"
            )
        previous = self._session_usage.get(session.session_id, {})
        delta = {
            key: value - previous.get(key, 0) for key, value in values.items()
        }
        if any(value < 0 for value in delta.values()):
            raise HarnessError("get_session_stats totals decreased")
        self._session_usage[session.session_id] = values
        for key, value in delta.items():
            self._transition_usage[key] += value
        context = data.get("contextUsage")
        cache_base = values["input"] + values["cache_read"]
        cache_ratio = values["cache_read"] / cache_base if cache_base else 0
        logger.info(
            "pi usage role=%s task=%s input=%s output=%s cache_read=%s cache_write=%s total=%s cost=%s cache_hit_ratio=%.4f context_usage=%s",
            role,
            task_slug,
            values["input"],
            values["output"],
            values["cache_read"],
            values["cache_write"],
            values["total"],
            values["cost"],
            cache_ratio,
            context,
        )

    def _step_slug(self) -> str:
        stem = os.path.splitext(os.path.basename(self.session_scope))[0]
        slug = stem.removeprefix("STEP-")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise HarnessError(
                "STEP file basename must be lowercase kebab-case for Pi naming"
            )
        return slug

    def _session_name(self, role: str, task_slug: str = "bootstrap") -> str:
        if role not in {"coordinator", "worker", "validator", "assessor"}:
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
        for attempt, idle_timeout_seconds in enumerate(_IDLE_TIMEOUT_SCHEDULE):
            try:
                return self._invoke_once(
                    role,
                    retry_prompt,
                    session,
                    task_slug,
                    idle_timeout_seconds,
                )
            except PiConfigurationError:
                raise
            except (PacketNormalizationError, FinalizerProtocolError) as exc:
                if finalization_retried:
                    raise
                # The role has completed its work but its result was not accepted.
                # Preserve the session and ask only for finalizer formatting.
                retry_prompt = build_finalization_prompt(role, exc)
                finalization_retried = True
            except (OSError, HarnessError) as exc:
                is_idle_timeout = (
                    str(exc) == "RPC idle timed out before settlement"
                )
                if is_idle_timeout:
                    logger.error(
                        "pi idle timeout role=%s task=%s attempt=%s timeout_seconds=%s",
                        role,
                        task_slug,
                        attempt + 1,
                        idle_timeout_seconds,
                    )
                    if attempt == len(_IDLE_TIMEOUT_SCHEDULE) - 1:
                        raise HarnessError(
                            f"{role} harness failure: {exc}"
                        ) from exc
                    # _invoke_once has already terminated and reaped this process.
                    # Reconnect with the same role session and replay the unpersisted
                    # task so Pi retains its cumulative session accounting.
                    retry_prompt = prompt
                elif attempt == len(_IDLE_TIMEOUT_SCHEDULE) - 1:
                    raise HarnessError(
                        f"{role} harness failure: {exc}"
                    ) from exc
                else:
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
                subprocess.run(
                    ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                logger.error("pi process-tree kill timed out pid=%s", proc.pid)
            except OSError as exc:
                logger.error(
                    "pi process-tree kill failed pid=%s error=%s", proc.pid, exc
                )
            return
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except OSError as exc:
            logger.error(
                "pi process-group kill failed pid=%s error=%s", proc.pid, exc
            )

    def _terminate_process(
        self,
        proc: subprocess.Popen[str],
        stderr_lines: queue.Queue[str | None],
    ) -> None:
        self._close_pipe(proc.stdin)
        try:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            logger.error("pi cleanup terminate timed out pid=%s", proc.pid)
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
        self._drain_pipe(stderr_lines)

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
        return _json_mapping(result.stdout)

    def _settings_for(self, role: str) -> dict[str, str]:
        try:
            return self.role_settings[role]
        except KeyError as exc:
            raise HarnessError(f"missing role settings for {role}") from exc

    @staticmethod
    def _configuration_error(
        role: str, settings: dict[str, str], stderr: str
    ) -> PiConfigurationError | None:
        detail = stderr.strip()
        if not detail or not re.search(r"\b(model|thinking)\b", detail, re.I):
            return None
        return PiConfigurationError(
            "Pi rejected role settings "
            f"role={role} model={settings['model']} "
            f"thinking={settings['thinking']}: {detail}. "
            "Correct the Pi model configuration or create a new STEP workflow."
        )

    def _invoke_once(
        self,
        role: str,
        prompt: str,
        session: RoleSession,
        task_slug: str,
        idle_timeout_seconds: float,
    ) -> dict[str, Any]:
        settings = self._settings_for(role)
        command = [
            *self.command,
            "--extension",
            str(self._extension_path()),
            "--step-role",
            role,
            "--model",
            settings["model"],
            "--thinking",
            settings["thinking"],
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
            finalizer_text, finalizer_details, finalizer_error, settled = (
                None,
                None,
                None,
                False,
            )
            streamed_blocks: dict[tuple[str, int], list[str]] = {}
            saw_streamed_content = False
            awaiting_stats = False
            while True:
                idle_remaining = idle_timeout_seconds - (
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
                event = json.loads(line)
                event_type = event.get("type")
                if event_type == "agent_start":
                    logger.info(
                        "pi agent started role=%s task=%s", role, task_slug
                    )
                elif event_type == "agent_end":
                    logger.info(
                        "pi agent ended role=%s task=%s will_retry=%s",
                        role,
                        task_slug,
                        event.get("willRetry", False),
                    )
                    if not saw_streamed_content:
                        for message in event.get("messages", []):
                            if (
                                not isinstance(message, dict)
                                or message.get("role") != "assistant"
                            ):
                                continue
                            for content in message.get("content", []):
                                if not isinstance(content, dict):
                                    continue
                                kind = content.get("type")
                                output = (
                                    content.get("thinking")
                                    if kind == "thinking"
                                    else content.get("text")
                                )
                                if kind in {"thinking", "text"} and isinstance(
                                    output, str
                                ):
                                    logger.debug(
                                        "pi %s end role=%s task=%s output=%s",
                                        kind,
                                        role,
                                        task_slug,
                                        _inline_debug_text(output),
                                    )
                elif event_type == "message_update":
                    update = event.get("assistantMessageEvent")
                    if isinstance(update, dict):
                        update_type = update.get("type")
                        match = re.fullmatch(
                            r"(thinking|text|toolcall)_(start|delta|end)",
                            str(update_type),
                        )
                        if match:
                            kind, phase = match.groups()
                            index = update.get("contentIndex")
                            content_index = (
                                index if isinstance(index, int) else 0
                            )
                            key = (kind, content_index)
                            if phase == "start":
                                streamed_blocks[key] = []
                                logger.debug(
                                    "pi %s start role=%s task=%s content_index=%s",
                                    kind,
                                    role,
                                    task_slug,
                                    content_index,
                                )
                            elif phase == "delta":
                                delta = update.get("delta")
                                if isinstance(delta, str):
                                    streamed_blocks.setdefault(key, []).append(
                                        delta
                                    )
                            else:
                                saw_streamed_content = True
                                output = update.get("content")
                                if not isinstance(output, str):
                                    output = "".join(
                                        streamed_blocks.get(key, [])
                                    )
                                streamed_blocks.pop(key, None)
                                if kind == "toolcall":
                                    output = _safe_debug_value(
                                        update.get("toolCall", output)
                                    )
                                else:
                                    output = _inline_debug_text(output)
                                logger.debug(
                                    "pi %s end role=%s task=%s content_index=%s output=%s",
                                    kind,
                                    role,
                                    task_slug,
                                    content_index,
                                    output,
                                )
                elif event_type == "tool_execution_start":
                    logger.debug(
                        "pi tool start role=%s task=%s name=%s args=%s",
                        role,
                        task_slug,
                        event.get("toolName", "unknown"),
                        _safe_debug_value(event.get("args", {})),
                    )
                elif event_type == "tool_execution_end":
                    if event.get("toolName") != f"stagger_step_finalize_{role}":
                        logger.debug(
                            "pi tool end role=%s task=%s name=%s is_error=%s result=%s",
                            role,
                            task_slug,
                            event.get("toolName", "unknown"),
                            event.get("isError", False),
                            _safe_debug_value(event.get("result")),
                        )
                elif event_type == "extension_error":
                    logger.error(
                        "pi extension error role=%s task=%s error=%s",
                        role,
                        task_slug,
                        event.get("error", "unknown"),
                    )
                elif event_type == "auto_retry_start":
                    logger.error(
                        "pi automatic retry role=%s task=%s attempt=%s error=%s",
                        role,
                        task_slug,
                        event.get("attempt", "unknown"),
                        event.get("errorMessage", "unknown"),
                    )
                if event_type == "agent_settled":
                    if awaiting_stats:
                        raise HarnessError(
                            "RPC settled while session stats were pending"
                        )
                    proc.stdin.write(
                        json.dumps(
                            {
                                "id": str(uuid.uuid4()),
                                "type": "get_session_stats",
                            }
                        )
                        + "\n"
                    )
                    proc.stdin.flush()
                    awaiting_stats = True
                    continue
                if (
                    event_type == "response"
                    and event.get("command") == "get_session_stats"
                ):
                    if not event.get("success"):
                        raise HarnessError(
                            str(event.get("error", "get_session_stats failed"))
                        )
                    self._record_session_stats(
                        role, task_slug, session, event.get("data")
                    )
                    settled = True
                    break
                if event_type == "response" and event.get("success") is False:
                    error = str(event.get("error", "RPC rejected request"))
                    configuration_error = self._configuration_error(
                        role, settings, error
                    )
                    if configuration_error is not None:
                        raise configuration_error
                    raise HarnessError(error)
                if (
                    event_type == "tool_execution_end"
                    and event.get("toolName") == f"stagger_step_finalize_{role}"
                ):
                    logger.debug(
                        "pi finalizer end role=%s task=%s is_error=%s",
                        role,
                        task_slug,
                        event.get("isError", False),
                    )
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
                    details = result.get("details")
                    finalizer_details = (
                        details if isinstance(details, dict) else None
                    )
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
            self._last_finalizer_details = finalizer_details
            logger.info(
                "pi settled role=%s session_name=%s session_id=%s",
                role,
                session.name,
                session_id,
            )
            return payload
        except (OSError, HarnessError) as exc:
            configuration_error = self._configuration_error(
                role, settings, self._drain_pipe(stderr_lines)
            )
            if configuration_error is not None:
                raise configuration_error from exc
            raise
        finally:
            self._terminate_process(proc, stderr_lines)


def _json_mapping(text: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise HarnessError(f"malformed role JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise HarnessError("role output must be a JSON object")
    return value
