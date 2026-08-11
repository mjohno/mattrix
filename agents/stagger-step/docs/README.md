# stagger-step

`stagger-step` owns the STEP YAML schema, validation, legal transitions, atomic approval writes, Markdown user reviews, and self-contained role prompts under `src/stagger_step/prompts/`.

## Deming cycle

Stagger Step advances its goal through small, evidence-based Deming PDCA cycles with Owner control between tasks:

- **Plan:** The Coordinator ranks proposals and recommends one next task.
- **Owner gate:** The Owner approves that recommendation or supplies revision feedback before work begins.
- **Do:** The Worker completes the approved task and records `work` summary and evidence.
- **Check:** The Validator independently checks the approved criteria and records the result and evidence in `validate`.
- **Act:** The Assessor records delivery learning in `retro`; the Coordinator uses it with the evidence and Owner feedback to plan the next task.

This separation keeps task selection, execution, validation, and delivery assessment independent while the Owner remains responsible for approval.

## Build output

All generated Stagger Step build artifacts belong in the repository-root `build/stagger-step/` directory. Run `python make.py build-stagger-step` to create its wheel there and `python make.py clean` to remove generated build, package, cache, and coverage artifacts. Build output is intentionally ignored by Git.

## CLI

```bash
STEP_FILE=STEP-example.yaml python -m stagger_step.cli init --goal "Ship the change" --change artifacts --commit
STEP_FILE=STEP-example.yaml python -m stagger_step.cli validate
printf '%s\n' 'packet: {work: {summary: Ran checks, evidence: []}}' | stagger-step normalize --role worker
printf '%s\n' 'packet: {validate: {result: success, summary: Checks passed, evidence: []}, clarification_request: null}' | stagger-step normalize --role validator
# One-shot approval promotes work, runs its cycle, and prints the next gate.
STEP_FILE=STEP-example.yaml python -m stagger_step.cli gate approved
# `session` keeps accepting responses in the same process until break or completion.
STEP_FILE=STEP-example.yaml python -m stagger_step.cli session
```

`init` creates bootstrap state and renders its owner review as Markdown on stdout. Only the exact input `approved` promotes the recommendation. Revision feedback must contain a letter and more than three non-whitespace characters; empty, whitespace-only, numeric, and punctuation-only input is ignored. `break` is read-only. `session` keeps the pending role output in process memory, so an arbitrary edited YAML gate can never be submitted as an approval. A manually edited state is accepted only through `validate_state`.

## Change path and commit mode

`init --change PATH` stores an optional root-level `change_path`. Relative paths are resolved from the STEP file, must name an existing directory, and are supplied to every role as its shared artifact location. The STEP file is the change record; no `CHANGE.md` is required.

`init --commit` stores root-level `commit_mode: true`; without it, `commit_mode` is false. Later `gate` and `session` commands inherit that setting. Pass `--commit-off` to either command to bypass commit behavior for that invocation or session without changing STEP state. Enabled commit mode requires the invoking directory to be a clean, non-bare Git worktree with no index lock and configured author and committer identity. The STEP file is excluded from packet staging.

A changed packet commits with Stagger Step's fixed message format:

```text
step: <slug>

Intent:
<intent>

Done:
<work.summary>

Verified:
<validate.summary>

Result: <success|partial|failure|blocked>
```

The subject is deterministically truncated to 50 characters; body content, including intent, is wrapped to 72 characters. Empty `Done` or `Verified` sections are omitted.

No-op packets advance without an empty commit. A commit failure leaves the packet awaiting approval; Stagger Step does not push, switch branches, rebase, merge, reset, or stash.

## AFK session mode

In `session`, enter `afk` at a manual gate to approve that gate and automatically approve later gates in the same process. AFK is never written to STEP state. A `blocked` result returns AFK to manual mode at the next gate. It also returns to manual mode when more than one of the last ten completed tasks is `failure`; before ten tasks complete, one failure is allowed. `partial` does not stop it. Ctrl+C while AFK also returns to manual mode. From manual mode, `break` exits the session and Ctrl+C keeps the normal crash/debug behavior.

## State and gates

Owner gates render as Markdown on stdout. They show the goal, applicable lessons and current-task results, ranked next tasks, and the recommendation, then prompt with `**Response:**`. Submitted responses are echoed and followed by `---` before the next review. The recommended next task is marked `**RECOMMENDED**`. Empty sections are omitted. YAML remains the persisted STEP state format.

Persisted state contains `version`, `goal`, optional `change_path`, `commit_mode`, `lessons`, completed `history`, the approved `current` task, and `completed`. Worker, Validator, Assessor, and Coordinator outputs are intentionally never persisted before owner approval. A gate contains `goal`, `lessons`, `history`, `current`, ranked `proposals`, `recommended`, and `completed`.

The coordinator selects durable gate lessons from existing lessons, completed history, and assessor actions. Approval validates the displayed gate, then atomically commits its completed current packet, coordinator-selected lessons, and recommended next packet (or terminal completion). The next `session` runs an approved active task through Worker → Validator → Assessor → Coordinator before returning to the human.

## Pi RPC adapter discovery

By default, the adapter starts an ephemeral Pi role session for each role in a STEP transition. It invokes Pi with a debuggable `--name STEP-<step-slug>-<task-slug>-<role>` and a random `--session-id`; the ID is reused for correction or clarification calls in that transition, but an idle timeout replaces it before replaying the task. It logs each session name and ID at INFO and never writes either to STEP state. The adapter loads the project-owned `pi-stagger-step` extension and selects one role through `--step-role`. It sends a JSONL `prompt`, waits for `agent_settled`, and accepts only the matching `stagger_step_finalize_<role>` tool result. That YAML is independently normalized through `stagger-step normalize --role <role>` before STEP processing. `--harness-session off` instead uses `--no-session`. A fresh subprocess is still started for each role invocation, role sessions remain distinct, and the adapter terminates the child before a user gate.

Supported discovery evidence: Pi RPC documents `prompt`, `tool_execution_end`, `agent_settled`, `abort`, `new_session`, and `get_state`; command rejection has `success: false`; missing, failed, or malformed finalizer output is a diagnosed harness error. The adapter resets its idle timeout whenever Pi emits JSONL output and applies a separate 30-minute maximum invocation duration. Idle timeouts use a fixed task-local schedule of 30, 60, then 120 seconds. Each timeout is logged as an error; after the first two, the adapter has already reaped the Pi process, discards its role session, and replays the unpersisted role task in a fresh session. The third timeout is terminal. After a rejected or missing finalizer, it sends a targeted finalization prompt rather than replaying the role packet. Other connection/process failures retry twice with bounded exponential backoff, and the adapter never infers a transition from a harness failure. Pi version/capabilities are not persisted in STEP state; callers may inspect RPC `get_state` diagnostics separately.

Stagger-step is execution-environment agnostic: its CLI and harness invoke the configured Pi RPC command without selecting host versus container policy. Deployment is responsible for supplying that command, the `stagger-step` executable available to `pi-stagger-step`, and its workspace boundary. No Pi RPC operation receives a STEP path or has state mutation authority.

## pi-stagger-step extension

The extension source is the packaged asset `src/stagger_step/pi_extension/index.ts`. The harness loads it explicitly for role processes and selects one role through `--step-role`; without that flag, the extension exposes no STEP-specific tool. Its LLM-visible tools are `stagger_step_finalize_coordinator`, `stagger_step_finalize_worker`, `stagger_step_finalize_validator`, and `stagger_step_finalize_assessor`; one role process receives only its matching tool. The wheel includes this asset, so a non-editable installation can invoke Pi-backed roles.

For interactive extension development, symlink its directory to `~/.pi/agent/extensions/pi-stagger-step`. The symlinked extension remains inert unless `--step-role` is supplied.

## Test boundaries and execution order

`tests/unit/` contains isolated validation, normalization, diagnostics, and harness invariants. `tests/integration/` contains local white-box component boundaries: `test_loop_transitions.py` composes `StepLoop` with state validation, while `test_user_paths.py` drives the CLI through a deterministic fake Pi JSONL executable. Run these deterministic local integration tests before adding focused units for uncovered risks.

`tests/integration/test_pi_rpc_live.py` is distinct Pi-facing, opt-in live black-box smoke coverage, not local integration coverage. It verifies one minimum real-Pi RPC finalizer capability and runs only when `PI_RPC_INTEGRATION=1`; schedule it after focused units and deterministic local integration. No live Pi service is required for the normal suite.

From the repository root, run the following order before considering a change verified:

```bash
python make.py format-check  # Black formatting check
python make.py ruff
python make.py pylint
python make.py mypy
pytest agents/stagger-step/tests/unit
pytest agents/stagger-step/tests/integration
PI_RPC_INTEGRATION=1 pytest agents/stagger-step/tests/integration/test_pi_rpc_live.py
python make.py build-stagger-step
python make.py docker-build
```

`python make.py quality` runs the Black, Ruff, Pylint, and mypy checks together. The live Pi test is opt-in and follows deterministic unit and local integration coverage; no live Pi service is required for the normal suite. The Python wheel and Docker builds verify their respective packaging paths.
