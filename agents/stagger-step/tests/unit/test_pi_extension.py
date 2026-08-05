from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[2]
EXTENSION = ROOT / "src/stagger_step/pi_extension/index.ts"
JITI = "/usr/lib/node_modules/@earendil-works/pi-coding-agent/node_modules/jiti"


def test_extension_exposes_typed_schemas_and_rejects_semantic_input():
    script = r"""
const createJiti = require(process.argv[1]);
const { Value } = require("typebox/value");
const extension = createJiti(process.argv[2])(process.argv[2]).default;
const tools = {};
const handlers = {};
let role = "worker";
extension({
  registerFlag() {},
  getFlag() { return role; },
  on(name, handler) { handlers[name] = handler; },
  registerTool(tool) { tools[role] = tool; },
});
handlers.session_start();
const worker = tools.worker;
worker.execute("test", {
  work_summary: " ",
  work_evidence: [],
  result: "success",
  validation_summary: "checked",
  validation_evidence: [],
}, new AbortController().signal).then((invalid) => {
  console.log(JSON.stringify({
    schema: worker.parameters,
    checks: {
      missing: Value.Check(worker.parameters, {}),
      wrong_type: Value.Check(worker.parameters, {
        work_summary: "worked", work_evidence: "not-a-list", result: "success",
        validation_summary: "checked", validation_evidence: [],
      }),
      invalid_enum: Value.Check(worker.parameters, {
        work_summary: "worked", work_evidence: [], result: "unknown",
        validation_summary: "checked", validation_evidence: [],
      }),
    },
    invalid,
  }));
});
"""
    result = subprocess.run(
        ["node", "-e", script, JITI, str(EXTENSION)],
        check=True,
        text=True,
        capture_output=True,
        env={
            **os.environ,
            "NODE_PATH": "/usr/lib/node_modules/@earendil-works/pi-coding-agent/node_modules",
        },
    )
    output = json.loads(result.stdout)

    schema = output["schema"]
    assert schema["required"] == [
        "work_summary",
        "work_evidence",
        "result",
        "validation_summary",
        "validation_evidence",
    ]
    assert schema["additionalProperties"] is False
    assert {value["const"] for value in schema["properties"]["result"]["anyOf"]} == {
        "success",
        "partial",
        "failure",
        "blocked",
    }
    assert output["checks"] == {
        "missing": False,
        "wrong_type": False,
        "invalid_enum": False,
    }
    assert output["invalid"]["isError"] is True
    assert "work_summary is required" in output["invalid"]["content"][0]["text"]
