from __future__ import annotations

import json
import logging
import os
import select
import subprocess
import time
import uuid
from dataclasses import dataclass
from typing import Any, Protocol


class HarnessError(RuntimeError):
    pass


logger = logging.getLogger("stagger_step.harness")


class Harness(Protocol):
    def invoke(
        self, role: str, prompt: str, *, follow_up: bool = False
    ) -> dict[str, Any]: ...
    def close(self) -> None: ...


@dataclass
class PiRpcHarness:
    """Run one short-lived Pi RPC process per role without exposing STEP files."""

    command: tuple[str, ...] = ("pi", "--mode", "rpc", "--no-session")
    timeout_seconds: float = 120.0
    retries: int = 2
    session_enabled: bool = False
    session_scope: str = ""

    def invoke(
        self, role: str, prompt: str, *, follow_up: bool = False
    ) -> dict[str, Any]:
        # A process is intentionally not shared across roles. `follow_up` is retained
        # solely for a same-role clarification in a future persistent-session adapter.
        del follow_up
        for attempt in range(self.retries + 1):
            try:
                return self._invoke_once(role, prompt)
            except (OSError, HarnessError) as exc:
                if attempt == self.retries:
                    raise HarnessError(f"{role} harness failure: {exc}") from exc
                logger.error(
                    "pi invocation retry role=%s attempt=%s error=%s",
                    role,
                    attempt + 1,
                    exc,
                )
                time.sleep(0.1 * (2**attempt))
        raise AssertionError("unreachable")

    def _invoke_once(self, role: str, prompt: str) -> dict[str, Any]:
        session_name = f"stagger-step-{role}"
        command = list(self.command)
        if self.session_enabled:
            command = [part for part in command if part != "--no-session"]
            session_id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL, f"stagger-step:{self.session_scope}:{role}"
                )
            )
            command.extend(("--session-id", session_id))
        else:
            session_id = session_name
        env = {
            key: value
            for key, value in os.environ.items()
            if key != "STEP_FILE" and not key.startswith("STAGGER_STEP_")
        }
        proc = subprocess.Popen(
            [*command, "--name", session_name],
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
            "pi rpc request session_id=%s payload=%s", session_id, json.dumps(request)
        )
        try:
            assert proc.stdin and proc.stdout
            proc.stdin.write(json.dumps(request) + "\n")
            proc.stdin.flush()
            deadline, text, settled = (
                time.monotonic() + self.timeout_seconds,
                None,
                False,
            )
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise HarnessError("RPC timed out before settlement")
                readable, _, _ = select.select([proc.stdout], [], [], remaining)
                if not readable:
                    raise HarnessError("RPC timed out before settlement")
                line = proc.stdout.readline()
                if not line:
                    raise HarnessError("RPC closed before settlement")
                logger.debug(
                    "pi rpc stdout session_id=%s payload=%s", session_id, line.rstrip()
                )
                event = json.loads(line)
                if event.get("type") == "agent_settled":
                    settled = True
                    break
                if event.get("type") == "response" and event.get("success") is False:
                    raise HarnessError(event.get("error", "RPC rejected request"))
                if event.get("type") == "agent_end":
                    for message in event.get("messages", []):
                        if message.get("role") == "assistant":
                            chunks = [
                                c.get("text", "")
                                for c in message.get("content", [])
                                if c.get("type") == "text"
                            ]
                            if chunks:
                                text = "".join(chunks)
            if not settled or text is None:
                raise HarnessError("RPC settled without assistant text")
            payload = _yaml_mapping(text)
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
