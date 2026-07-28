# stagger-step

`stagger-step` owns the STEP YAML schema, validation, legal transitions, atomic approval writes, and YAML user gates. `skills/src/map/step` supplies only role prompt and packet contracts.

## CLI

```bash
STEP_FILE=STEP-example.yaml python -m stagger_step.cli init --goal "Ship the change"
STEP_FILE=STEP-example.yaml python -m stagger_step.cli validate
# `session` renders the YAML gate, then accepts the human response in the same process.
STEP_FILE=STEP-example.yaml python -m stagger_step.cli session
```

`init` creates bootstrap state. Thereafter, only the exact input `approved` writes state. `break` and revisions are read-only. `session` keeps the pending role output in process memory, so an arbitrary edited YAML gate can never be submitted as an approval. A manually edited state is accepted only through `validate_state`.

## State and gates

Persisted state contains `version`, `goal`, `lessons`, completed `history`, an approved `active_packet`, and `completed`. Pending coordinator/assessor outputs are intentionally never persisted. A gate contains `goal`, `lessons`, `current_packet`, ranked `proposed_next_packets`, and `recommendation`.

The coordinator selects durable gate lessons from existing lessons, completed history, and assessor actions. Approval validates the displayed gate, then atomically commits its completed current packet, coordinator-selected lessons, and recommended next packet (or terminal completion). The next `session` runs an approved active task through worker → assessor → coordinator before returning to the human.

## Pi RPC adapter discovery

The adapter uses `pi --mode rpc --no-session --name stagger-step-<role>`, sends a JSONL `prompt`, waits for `agent_end`/`agent_settled`, extracts assistant text, and parses YAML. A fresh subprocess is started for each role invocation, so it cannot carry cross-role context. The adapter terminates it before a user gate.

Supported discovery evidence: Pi RPC documents `prompt`, `abort`, `new_session`, `get_state`, and `agent_settled`; command rejection has `success: false`; malformed YAML is a diagnosed harness error. Adapter retries connection/process failures twice with bounded exponential backoff and never infers a transition from a harness failure. Pi version/capabilities are not persisted in STEP state; callers may inspect RPC `get_state` diagnostics separately.

Stagger-step is execution-environment agnostic: its CLI and harness invoke the configured Pi RPC command without selecting host versus container policy. Deployment is responsible for supplying that command and its workspace boundary. No Pi RPC operation receives a STEP path or has state mutation authority.

`tests/integration/` is the primary user-path suite: it drives the CLI through a fake Pi JSONL executable. `tests/unit/` contains stable state and transition edge contracts. Run fast tests with `pytest`; set `PI_RPC_INTEGRATION=1` to run the marked live Pi RPC compatibility test, which sends one constrained YAML prompt.
