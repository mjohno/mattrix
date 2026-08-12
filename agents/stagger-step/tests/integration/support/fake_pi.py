#!/usr/bin/env python3
"""Deterministic JSONL Pi stand-in for CLI integration scenarios."""

from __future__ import annotations

import json
import os
import signal
import sys
import time
from pathlib import Path


def _finalizer_response(role: str, reply: object) -> object:
    """Adapt legacy fixtures to the current role finalizer output."""
    if not isinstance(reply, dict):
        return reply
    if role == "worker" and isinstance(reply.get("packet"), dict):
        return {"work": reply["packet"].get("work")}
    if role == "assessor" and "current_packet" in reply:
        return {
            "retro": reply.get("retro"),
            "clarification_requests": (
                [{"target": "worker", "request": "Provide missing evidence."}]
                if reply.get("clarification_needed")
                else []
            ),
        }
    return reply


def main() -> int:
    name = next(
        (
            sys.argv[index + 1]
            for index, arg in enumerate(sys.argv)
            if arg == "--name"
        ),
        "unknown",
    )
    role = name.rsplit("-", 1)[-1]
    scenario = json.loads(Path(os.environ["FAKE_PI_SCENARIO"]).read_text())
    request = json.loads(sys.stdin.readline())
    log_path = Path(os.environ["FAKE_PI_LOG"])
    prior = (
        [json.loads(line) for line in log_path.read_text().splitlines()]
        if log_path.exists()
        else []
    )
    index = sum(entry["role"] == role for entry in prior)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as stream:
        stream.write(
            json.dumps(
                {
                    "role": role,
                    "prompt": request["message"],
                    "step_file": os.getenv("STEP_FILE"),
                    "argv": sys.argv,
                }
            )
            + "\n"
        )
        stream.flush()
    startup_error = scenario.get("startup_errors", {}).get(role)
    if isinstance(startup_error, str):
        print(startup_error, file=sys.stderr, flush=True)
        return 2
    rpc_error = scenario.get("rpc_errors", {}).get(role)
    if isinstance(rpc_error, str):
        print(
            json.dumps(
                {"type": "response", "success": False, "error": rpc_error}
            ),
            flush=True,
        )
        return 0
    replies = scenario.get(role)
    if replies is None and role == "validator":
        # Legacy scenarios predate the independent Validator phase. Preserve
        # their recorded validation outcome while routing it through Validator.
        worker_reply = scenario.get("worker", [])[index]
        worker_packet = (
            worker_reply.get("packet", {})
            if isinstance(worker_reply, dict)
            else {}
        )
        reply = {
            "validate": worker_packet.get(
                "validate",
                {
                    "result": "success",
                    "summary": "Legacy fixture validation",
                    "evidence": ["legacy fixture"],
                },
            ),
            "clarification_request": None,
        }
    else:
        reply = replies[index]
    thinking = None
    writes = None
    if isinstance(reply, dict):
        reply = dict(reply)
        thinking = reply.pop("_thinking", None)
        writes = reply.pop("_write", None)
    if writes is not None:
        for path, content in writes.items():
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
    if reply == "close":
        return 0
    if reply == "interrupt":
        os.kill(os.getppid(), signal.SIGINT)
        time.sleep(0.1)
        return 0
    if reply == "sleep":
        time.sleep(30)
        return 0
    print(
        json.dumps(
            {
                "id": request["id"],
                "type": "response",
                "command": "prompt",
                "success": True,
            }
        ),
        flush=True,
    )
    if reply == "heartbeat":
        for _ in range(3):
            print(json.dumps({"type": "extension_ui_request"}), flush=True)
            time.sleep(0.1)
        return 0
    reply = _finalizer_response(role, reply)
    text = reply if isinstance(reply, str) else json.dumps(reply)
    if isinstance(thinking, str):
        print(
            json.dumps(
                {
                    "type": "message_update",
                    "assistantMessageEvent": {
                        "type": "thinking_start",
                        "contentIndex": 0,
                    },
                }
            ),
            flush=True,
        )
        print(
            json.dumps(
                {
                    "type": "message_update",
                    "assistantMessageEvent": {
                        "type": "thinking_delta",
                        "contentIndex": 0,
                        "delta": thinking,
                    },
                }
            ),
            flush=True,
        )
        print(
            json.dumps(
                {
                    "type": "message_update",
                    "assistantMessageEvent": {
                        "type": "thinking_end",
                        "contentIndex": 0,
                    },
                }
            ),
            flush=True,
        )
    if reply != "no_finalizer":
        tool_name = (
            "stagger_step_finalize_wrong"
            if reply == "wrong_finalizer"
            else f"stagger_step_finalize_{role}"
        )
        print(
            json.dumps(
                {
                    "type": "tool_execution_end",
                    "toolName": tool_name,
                    "result": {
                        "content": [{"type": "text", "text": text}],
                        "details": {"canonical": reply},
                        "isError": False,
                    },
                }
            ),
            flush=True,
        )
    print(
        json.dumps(
            {
                "type": "agent_end",
                "messages": [
                    {
                        "role": "assistant",
                        "content": [
                            {"type": "text", "text": "ignored assistant text"}
                        ],
                    }
                ],
            }
        ),
        flush=True,
    )
    if reply != "unsettled":
        print(json.dumps({"type": "agent_settled"}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
