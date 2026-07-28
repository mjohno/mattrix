# SPEC-mattrix: Mattrix Agentic Operating Engine

## 1. Purpose

- PUR-001: Establish Mattrix as Matt's agentic operating engine: a maintainable home for reusable skills, knowledge-base contracts, and deterministic agents without conflating it with business data.
- PUR-002: Refactor the existing `skills` project so the STEP protocol can be operated as a deterministic, approval-governed loop by an agent while retaining human review at defined boundaries.

## 2. Current State Summary

- CUR-001: The current repository is named `skills` and contains its skill source under `src/` and its supporting documentation under `docs/`.
- CUR-002: `src/map/step` defines a STEP protocol and authoritative `step_cli.py` state interface, including start, context, approve, record, gate, and lint operations.
- CUR-003: The current project does not yet contain first-class `kb/` or `agents/` domains.

## 3. Future State

- FUT-001: The Mattrix repository is a monorepo with independently bounded `skills/`, `kb/`, and `agents/` top-level domains.
- FUT-002: `skills/` contains the current skill package source and documentation at `skills/src/` and `skills/docs/`.
- FUT-003: `skills/src/interface/knowledge-base/` owns the reusable MKF contract; `kb/src/` implements that contract and `kb/docs/` documents it.
- FUT-004: `agents/stagger-step/` is the initial agent product and has separate `src/`, `docs/`, and `tests/` roots; `agents/rfc/` is deferred until it has a concrete responsibility.
- FUT-005: `agents/stagger-step` owns STEP state and a deterministic transition loop. Given a valid STEP file and exact user input, it selects one legal transition or returns an explicit non-executing error.
- FUT-006: `skills/map/step/` defines role-specific context and packet-normalization contracts for coordinator, worker, and assessor subagents; it does not own STEP state.
- FUT-007: The loop presents approval gates as YAML containing the goal, lessons, pending current packet, ranked proposed-next packets, and recommendation.
- FUT-008: Pi.dev is a replaceable RPC execution harness. It runs isolated coordinator, worker, and assessor sessions while `agents/stagger-step` retains state, transition, and gate ownership.

## 4. Scope

### In Scope

- SCP-IN-001: Rename and reframe the repository as `mattrix`.
- SCP-IN-002: Introduce the monorepo domain layout for `skills`, `kb`, and `agents`.
- SCP-IN-003: Relocate the existing project contents beneath the `skills/` domain while preserving its package behavior and documentation.
- SCP-IN-004: Define the role-specific coordinator, worker, and assessor context and packet-normalization contract in `skills/map/step/`.
- SCP-IN-005: Define the deterministic `agents/stagger-step` loop, including STEP state ownership, CLI bootstrap, user approval, legal transitions, and failure handling.
- SCP-IN-006: Establish the sequential loop boundary: coordinator → worker → assessor → coordinator → user, with the loop mediating every exchange.
- SCP-IN-007: Define and validate a replaceable Pi.dev RPC harness adapter for subagent execution.

### Out of Scope

- SCP-OUT-001: Migrating Mattrix domains into separate repositories.
- SCP-OUT-002: Storing business data, business-domain knowledge, or production application data in Mattrix.
- SCP-OUT-003: Implementing arbitrary autonomous execution without the STEP protocol's required human approval gates.
- SCP-OUT-004: Defining `agents/rfc/` or other future agents before they have a concrete responsibility.
- SCP-OUT-005: Giving coordinator, worker, or assessor subagents direct STEP-state access or direct communication with each other.
- SCP-OUT-006: Preventing manual YAML state edits; they remain an explicit human escape hatch subject to loop validation.

## 5. Requirements

- REQ-001: The root layout shall contain independently bounded `skills/`, `kb/`, and `agents/` domains; each owns source and documentation, and each implemented agent additionally owns tests.
- REQ-002: `skills/src/interface/knowledge-base/` shall own the MKF contract and `kb/src/` shall implement it; dependency direction is `agents`/`kb` → `skills`, never from skills or KB to an individual agent.
- REQ-003: `skills/map/step/` shall provide only role-specific coordinator, worker, and assessor instructions plus shared packet-normalization tooling. Each subagent loads its own role reference and the shared packet contract.
- REQ-004: `agents/stagger-step` shall own STEP-file schema, state validation, legal transitions, and its CLI entry point. `STEP_FILE` identifies the file to resume or create; a goal is required to create a new file.
- REQ-005: The loop shall be the only STEP-state authority. It shall invoke subagents one at a time and mediate every exchange; subagents shall neither invoke STEP operations nor communicate directly.
- REQ-006: The worker may modify its assigned workspace and shall return structured Do and Validate evidence. The assessor shall normalize worker output, may request one worker clarification round through the loop, and shall assess whether the completed work moved the workflow closer to its goal. Its retro shall record wins as effective progress, issues as friction, failure, or lack of progress, and proposed actions; it shall recommend outcome, lessons, and ranked next packets to the coordinator.
- REQ-007: Given the goal, lessons, current progress, and assessor-proposed actions, the coordinator shall produce initial and post-work ranked next-best-task YAML gate packets. A gate shall contain `goal`, `lessons`, `current_packet`, ranked `proposed_next_packets`, and `recommendation`; a fresh gate has no current packet.
- REQ-008: Exact `approved` is the only state-changing input. It shall validate the packet and legal transition, atomically commit the pending current packet and lessons, and approve the selected next task; with no next task it shall also complete the workflow.
- REQ-009: Exact `break` and every revision command shall write nothing. Revisions may change only lessons and proposed-next packets; the coordinator must produce a fresh gate. Resuming an unapproved workflow shall regenerate proposals from persisted state.
- REQ-010: Packet-normalization tooling and the loop shall both validate packet shape; the loop shall additionally validate state shape and transitions. Invalid, incomplete, ambiguous, or blocked input shall produce an explicit non-executing outcome.
- REQ-011: A manually edited STEP file shall be accepted as authoritative only when it passes loop validation.
- REQ-012: Pi.dev integration shall be isolated behind an `agents/stagger-step` harness adapter. The adapter shall execute subagents but shall not own STEP state, transition selection, or user-gate behavior.
- REQ-013: The harness shall create a distinct Pi session for each coordinator, worker, or assessor invocation. It may reuse a session only for a same-role follow-up; the loop alone carries context across roles.
- REQ-014: The harness shall provide each subagent role-specific system or context prompts, inline execution context, and path references. It shall not provide another role's private context or STEP-state operations.
- REQ-015: A Pi execution session shall end when control returns to the loop for a user gate. A later approved task shall start a new applicable Pi session.
- REQ-016: Workers shall initially use Pi's built-in capabilities in a Docker container. Connection failures may use bounded exponential-backoff retries; malformed data shall return diagnosable failure output rather than inferred state changes.

## 6. Acceptance

- ACC-001: Repository inspection confirms `skills/src/`, `skills/docs/`, `kb/src/`, `kb/docs/`, and the implemented `agents/stagger-step/{src,docs,tests}` layout; `agents/rfc/` is absent.
- ACC-002: Documentation distinguishes `skills/map/step` role/packet contracts from `agents/stagger-step` state and transition ownership.
- ACC-003: A transition table or executable contract demonstrates one legal loop outcome for every valid STEP state and exact gate input, including fresh, approved, terminal, paused, revised, invalid, and blocked paths.
- ACC-004: Tests demonstrate that no STEP file write occurs before exact `approved`, and that an approval atomically commits the pending extracted packet, lessons, and selected next task or terminal completion.
- ACC-005: Tests demonstrate coordinator → worker → assessor → coordinator sequencing, no direct subagent interaction, one clarification-round maximum, and no subagent STEP access.
- ACC-006: Tests demonstrate duplicate packet validation, loop state/transition validation, and acceptance or explicit rejection of manually edited YAML.
- ACC-007: The repository contains no business-data storage contract presented as a responsibility of Mattrix.
- ACC-008: Tests demonstrate that the Pi harness cannot mutate STEP state, that sessions are isolated by role, and that the loop is the sole cross-role mediator.
- ACC-009: Fast tests exercise a mock Pi RPC adapter, and vertical-slice tests exercise the supported real Pi RPC server.

## 7. Quality

### Constraints / Non-Negotiables

- QUA-CON-001: Human review remains mandatory at STEP approval boundaries.
- QUA-CON-002: `agents/stagger-step` is the sole runtime STEP-state authority; only exact `approved` may write state, while valid manual YAML edits remain an explicit human escape hatch.
- QUA-CON-003: Domain boundaries must permit future repository extraction without requiring behavioral redesign.
- QUA-CON-004: Skills resolve package paths relative to their `SKILL.md`; documentation resolves paths relative to its `docs/` directory.
- QUA-CON-005: Pi.dev-specific RPC details shall not leak into STEP state, role contracts, or deterministic transition logic.

### Priorities

- QUA-PRI-001: Deterministic, explainable state transitions take precedence over agent autonomy or convenience.
- QUA-PRI-002: Clear ownership and dependency direction take precedence over minimizing the initial number of directories.
- QUA-PRI-003: The monorepo remains lean: shared tooling and contracts are centralized only when they genuinely serve multiple domains.

## 8. Expectations

- EXP-001: Implementation shall trace structural work to FUT-001 through FUT-004 and loop behavior to FUT-005 through FUT-007 and REQ-003 through REQ-011.
- EXP-002: The clean-break relocation shall move first; observed relative-path violations shall be repaired without compatibility wrappers or a separate pre-migration inventory.
- EXP-003: The loop design shall be reviewed before implementation for missing transitions, ambiguous gate inputs, invalid packet handling, and cross-domain boundary violations.
- EXP-004: A Pi.dev discovery spike shall establish the supported RPC operations, session lifecycle, cancellation/error behavior, compatibility policy, and permitted non-authoritative observability before adapter implementation.

## 9. Uncertainties

### Risks

- UNC-RISK-001: Relocation could expose an incorrectly rooted path; accepted mitigation is to repair observed violations because package and documentation paths are intended to be local-relative.
- UNC-RISK-002: Coordinator or assessor output could drift from the required packet contract; packet normalization plus independent loop validation mitigates this risk.
- UNC-RISK-003: Shared tooling could become premature infrastructure; packet-normalization tooling remains in `skills/map/step` until a separate consumer proves a broader contract is needed.
- UNC-RISK-004: Pi RPC or session behavior could make the intended harness lifecycle impossible or unreliable; contain it behind the adapter and resolve it through a discovery spike.

### Questions

- UNC-Q-001: Resolved — `skills/map/step` exposes role-specific context and packet-normalization tooling, not a library or STEP state interface.
- UNC-Q-002: Resolved — only the STEP file and exact user input determine loop transitions; subagent work remains intentionally nondeterministic.
- UNC-Q-003: Resolved — `kb/src/` implements MKF using the contract in `skills/src/interface/knowledge-base/`.
- UNC-Q-004: Resolved — no old-path compatibility is retained; this is a clean break.
- UNC-Q-005: Open — which Pi.dev RPC operations create sessions, send role prompts, collect output, cancel work, and report completion/errors?
- UNC-Q-006: Open — how do Pi session closure, resume, reconnect, capability/version mismatch, and non-authoritative diagnostic output behave in the supported runtime?

### Assumptions

- UNC-ASM-001: Confirmed — Mattrix is single-owner and requires no domain-specific access boundary now.
- UNC-ASM-002: Confirmed — cross-domain changes are expected and benefit from atomic monorepo changes.
- UNC-ASM-003: Confirmed — `agents/stagger-step` is the first concrete consumer and defines the initial boundary.

### Pre-Work Needed

- UNC-PRE-001: Resolved — no separate relocation inventory is required.
- UNC-PRE-002: Required — express and test the complete loop transition model and its error outcomes.
- UNC-PRE-003: Resolved — document the role-specific packet contract and `agents/stagger-step` state boundary.
- UNC-PRE-004: Resolved — initialize KB around its MKF implementation; defer `agents/rfc/`.
- UNC-PRE-005: Required — spike Pi.dev RPC integration using mocks and a real server; document the adapter contract, session lifecycle, failure policy, compatibility, and observability findings.

## 10. Decisions

- DEC-001: Accepted — adopt `mattrix` as the repository identity for Matt's agentic operating engine.
- DEC-002: Accepted — use a monorepo with `skills/`, `kb/`, and `agents/` as independently bounded domains; defer repository separation until independent ownership, release, access, or lifecycle needs are real.
- DEC-003: Accepted — `skills/map/step` owns reusable role and packet-normalization context; `agents/stagger-step` owns STEP state, transitions, and the deterministic loop.
- DEC-004: Accepted — the loop is the only mediator and runtime state authority; coordinator, worker, and assessor run sequentially and never directly interact.
- DEC-005: Accepted — exact `approved` is the only loop write and atomically commits the displayed packet and next-task approval; `break` and revisions never write.
- DEC-006: Accepted — user gates are YAML with goal, lessons, pending current packet, ranked proposed-next packets, and recommendation.
- DEC-007: Accepted — humans revise only lessons and proposed-next packets through gates; valid manual YAML edits are the explicit state-edit escape hatch.
- DEC-008: Accepted — initial and resumed unapproved workflows regenerate ranked proposals without persisting a pending proposal.
- DEC-009: Accepted — `kb/src/` implements MKF from `skills/src/interface/knowledge-base/`; `agents/rfc/` is deferred.
- DEC-010: Accepted — Pi.dev is a replaceable execution harness; `agents/stagger-step` remains the state-machine and user-gate owner.
- DEC-011: Accepted — Pi sessions are distinct by role and invocation, with same-role reuse permitted only for follow-up work; the loop alone carries cross-role context.
- DEC-012: Accepted — harness integration uses mocks for fast feedback and real-server vertical-slice tests.
