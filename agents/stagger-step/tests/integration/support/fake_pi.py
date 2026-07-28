#!/usr/bin/env python3
"""Deterministic JSONL Pi stand-in for CLI integration scenarios."""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

def main() -> int:
    role = next((arg.removeprefix("stagger-step-") for arg in sys.argv if arg.startswith("stagger-step-")), "unknown")
    scenario = json.loads(Path(os.environ["FAKE_PI_SCENARIO"]).read_text())
    request = json.loads(sys.stdin.readline())
    log_path = Path(os.environ["FAKE_PI_LOG"])
    prior = [json.loads(line) for line in log_path.read_text().splitlines()] if log_path.exists() else []
    index = sum(entry["role"] == role for entry in prior)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as stream:
        stream.write(json.dumps({"role": role, "prompt": request["message"], "step_file": os.getenv("STEP_FILE")}) + "\n")
    reply = scenario[role][index]
    if reply == "close": return 0
    print(json.dumps({"id": request["id"], "type": "response", "command": "prompt", "success": True}), flush=True)
    text = reply if isinstance(reply, str) else json.dumps(reply)
    print(json.dumps({"type": "agent_end", "messages": [{"role": "assistant", "content": [{"type": "text", "text": text}]}]}), flush=True)
    if reply != "unsettled": print(json.dumps({"type": "agent_settled"}), flush=True)
    return 0
if __name__ == "__main__": raise SystemExit(main())
