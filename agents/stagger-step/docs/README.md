# stagger-step

`stagger-step` owns the STEP YAML schema, validation, legal transitions, atomic approval writes, and YAML user gates. `skills/src/map/step` supplies only role prompt and packet contracts.

## CLI

```bash
STEP_FILE=STEP-example.yaml python -m stagger_step.cli init --goal "Ship the change"
STEP_FILE=STEP-example.yaml python -m stagger_step.cli validate
printf '%s\n' 'packet: {slug: validate-cli, intent: Validate CLI, criteria: [checks], do: {summary: Ran checks, evidence: []}, validate: {result: success, evidence: []}}' | stagger-step normalize --role worker
# One-shot approval promotes work, runs its cycle, and prints the next gate.
STEP_FILE=STEP-example.yaml python -m stagger_step.cli gate approved
# `session` keeps accepting responses in the same process until break or completion.
STEP_FILE=STEP-example.yaml python -m stagger_step.cli session
```

`init` creates bootstrap state. Thereafter, only the exact input `approved` writes state. `break` and revisions are read-only. `session` keeps the pending role output in process memory, so an arbitrary edited YAML gate can never be submitted as an approval. A manually edited state is accepted only through `validate_state`.

## State and gates

Persisted state contains `version`, `goal`, `lessons`, completed `history`, an approved `active_packet`, and `completed`. Pending coordinator/assessor outputs are intentionally never persisted. A gate contains `goal`, `lessons`, `current_packet`, ranked `proposed_next_packets`, and `recommendation`.

The coordinator selects durable gate lessons from existing lessons, completed history, and assessor actions. Approval validates the displayed gate, then atomically commits its completed current packet, coordinator-selected lessons, and recommended next packet (or terminal completion). The next `session` runs an approved active task through worker → assessor → coordinator before returning to the human.

## Pi RPC adapter discovery

By default, the adapter uses persistent role sessions: it invokes Pi with `--name STEP-<slug>-<role>`, a stable role- and STEP-file-specific UUID `--session-id`, the project-owned `pi-stagger-step` extension, and a harness-selected `--step-role`. It sends a JSONL `prompt`, waits for `agent_settled`, and accepts only the matching `stagger_step_finalize_<role>` tool result. That YAML is independently normalized through `stagger-step normalize --role <role>` before STEP processing. It logs the coordinator, worker, and assessor UUIDs at INFO but never writes them to STEP state. `--harness-session off` instead uses `--no-session`. A fresh subprocess is still started for each role invocation, role sessions remain distinct, and the adapter terminates the child before a user gate.

Supported discovery evidence: Pi RPC documents `prompt`, `tool_execution_end`, `agent_settled`, `abort`, `new_session`, and `get_state`; command rejection has `success: false`; missing, failed, or malformed finalizer output is a diagnosed harness error. Adapter retries connection/process failures twice with bounded exponential backoff and never infers a transition from a harness failure. Pi version/capabilities are not persisted in STEP state; callers may inspect RPC `get_state` diagnostics separately.

Stagger-step is execution-environment agnostic: its CLI and harness invoke the configured Pi RPC command without selecting host versus container policy. Deployment is responsible for supplying that command, the `stagger-step` executable available to `pi-stagger-step`, and its workspace boundary. No Pi RPC operation receives a STEP path or has state mutation authority.

## pi-stagger-step extension

The extension source is `src/pi-extension/index.ts`. The harness loads it explicitly for role processes and selects one role through `--step-role`; without that flag, the extension exposes no STEP-specific tool. Its LLM-visible tools are `stagger_step_finalize_coordinator`, `stagger_step_finalize_worker`, and `stagger_step_finalize_assessor`; one role process receives only its matching tool.

For interactive extension development, symlink its directory to `~/.pi/agent/extensions/pi-stagger-step`. The symlinked extension remains inert unless `--step-role` is supplied.

## Test boundaries and execution order

`tests/unit/` contains isolated validation, normalization, diagnostics, and harness invariants. `tests/integration/` contains local white-box component boundaries: `test_loop_transitions.py` composes `StepLoop` with state validation, while `test_user_paths.py` drives the CLI through a deterministic fake Pi JSONL executable. Run these deterministic local integration tests before adding focused units for uncovered risks.

`tests/integration/test_pi_rpc_live.py` is distinct Pi-facing, opt-in live black-box smoke coverage, not local integration coverage. It verifies one minimum real-Pi RPC finalizer capability and runs only when `PI_RPC_INTEGRATION=1`; schedule it after focused units and deterministic local integration. No live Pi service is required for the normal suite.
