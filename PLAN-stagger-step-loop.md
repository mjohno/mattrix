# Plan: Stagger Step Python CLI and STEP Role Refactor

PLAN_ID: PLAN-stagger-step-loop
Source: SPEC-mattrix.md
Purpose: Replace the current monolithic STEP CLI model with a Python CLI project that owns deterministic loop state and uses skill-provided role and normalization contracts.

## Source Summary

- FUT-005 through FUT-007: `agents/stagger-step` owns STEP state and deterministic transitions; `skills/map/step` owns role context and packet normalization; gates are YAML.
- REQ-003 through REQ-011: The loop mediates coordinator, worker, and assessor; only exact `approved` writes state; `break` and revisions do not write; manual YAML remains a validated escape hatch.
- ACC-003 through ACC-006: The transition model, atomic approvals, sequential subagents, and validation boundaries require executable tests.
- FUT-008 and REQ-012 through REQ-016: Pi.dev is a replaceable RPC harness with role-isolated sessions; its concrete RPC behavior requires discovery before adapter implementation.

## Gap Map

| Gap ID | Source Summary | Current Problem | Target State |
| --- | --- | --- | --- |
| GAP-1 | CUR-002, FUT-005, DEC-003 | `src/map/step/scripts/step_cli.py` combines STEP state, protocol, and CLI responsibilities in the skills domain. | `agents/stagger-step` is a Python CLI project that owns STEP-file schema, state validation, transitions, and CLI entry. |
| GAP-2 | FUT-006, REQ-003, REQ-006 | Coordinator, worker, and assessor context and normalized packet shapes are not yet separated into role contracts. | `skills/map/step` contains role-specific references and a shared packet-normalization CLI for those subagents. |
| GAP-3 | REQ-005 through REQ-009 | The required sequential mediation, YAML gate, exact approval write rule, and revision behavior are not represented by the target loop. | The loop enforces coordinator → worker → assessor → coordinator → user and writes only on exact `approved`. |
| GAP-4 | REQ-010, REQ-011, ACC-003 through ACC-006 | Packet/state validation and manual-edit handling lack the target executable coverage. | The Python CLI independently validates packets, state, and transitions and has tests for every required path. |
| GAP-5 | FUT-008, REQ-012 through REQ-016, UNC-Q-005, UNC-Q-006 | The supported Pi RPC surface, session lifecycle, compatibility, and failure/observability behavior are unknown. | A replaceable Pi harness adapter has a documented, tested contract and keeps all STEP authority in the loop. |

## Work Plan

### PLAN-stagger-step-loop-1 — Define STEP role and packet contracts in skills
Closes: GAP-2
Source refs: FUT-006, REQ-003, REQ-006, REQ-007
Status: todo
Depends on: PLAN-mattrix-structure-2
Outcome: Coordinator, worker, and assessor can load only the context needed for their role and return compatible structured packets.

Deliverables:
- Role-specific coordinator, worker, and assessor references under `skills/src/map/step/`.
- Shared packet contract covering worker Do/Validate evidence, assessor outcome/retro/lessons/actions, and coordinator gate proposals.
- YAML normalization CLI in `skills/src/map/step/scripts/` that converts semi-structured role output into validated packets.

Done when:
- Each role can load its own reference plus the shared packet contract without STEP-state instructions.
- Assessor guidance explicitly evaluates movement toward the goal, wins, issues, retro, and coordinator actions.
- The normalization CLI rejects malformed role packets and emits the required packet shape.

### PLAN-stagger-step-loop-2 — Scaffold the stagger-step Python CLI project
Closes: GAP-1
Source refs: FUT-004, FUT-005, REQ-004
Status: todo
Depends on: PLAN-mattrix-structure-1
Outcome: `agents/stagger-step` has an executable, testable Python CLI foundation with explicit state ownership.

Deliverables:
- Python project metadata and CLI entry point under `agents/stagger-step/src/`.
- CLI documentation under `agents/stagger-step/docs/`.
- Test harness under `agents/stagger-step/tests/`.
- `STEP_FILE` bootstrap behavior for create-with-goal and resume-existing paths.

Done when:
- The CLI can create a new STEP file when `STEP_FILE` names a new path and a goal is supplied.
- The CLI can load and validate an existing STEP file.
- No component under `skills/map/step` owns or mutates the stagger-step state file.

### PLAN-stagger-step-loop-3 — Implement deterministic state and approval transitions
Closes: GAP-1, GAP-3
Source refs: FUT-005, REQ-004, REQ-008, REQ-009, DEC-005, DEC-008
Status: todo
Depends on: PLAN-stagger-step-loop-2
Outcome: The Python CLI has one legal non-executing or state-transition outcome for each supported state and exact gate input.

Deliverables:
- STEP-file schema and transition model owned by the Python CLI.
- Atomic approval operation that commits the pending current packet, lessons, and selected next task or terminal completion.
- Read-only handling for `break` and revision commands.
- YAML gate renderer containing goal, lessons, current packet, ranked proposed-next packets, and recommendation.

Done when:
- No STEP file write occurs before exact `approved`.
- A fresh or resumed unapproved workflow regenerates ranked proposals without persisting a pending proposal.
- `approved`, `break`, revision, terminal, invalid, and blocked paths have explicit defined outcomes.

### PLAN-stagger-step-loop-4 — Discover the Pi.dev RPC harness contract
Closes: GAP-5
Source refs: FUT-008, REQ-012 through REQ-016, UNC-Q-005, UNC-Q-006, UNC-PRE-005
Status: todo
Depends on: PLAN-stagger-step-loop-2
Outcome: The supported Pi RPC integration surface and adapter contract are evidenced before production orchestration depends on them.

Deliverables:
- Discovery record for session creation, role prompting, output collection, cancellation, completion, and error reporting.
- Findings for session closure/resume/reconnect, capability/version compatibility, and permitted non-authoritative diagnostics.
- Mock and real-server spike fixtures.

Done when:
- The supported Pi RPC operations and lifecycle are documented from executable evidence.
- The adapter's retry, malformed-data, and diagnostic behavior is explicitly decided from the findings.
- Discovery identifies any Pi limitation that blocks the required isolated-role session model.

### PLAN-stagger-step-loop-5 — Implement Pi-mediated subagent orchestration
Closes: GAP-2, GAP-3, GAP-5
Source refs: SCP-IN-006, REQ-005, REQ-006, REQ-007, REQ-012 through REQ-016
Status: todo
Depends on: PLAN-stagger-step-loop-1, PLAN-stagger-step-loop-3, PLAN-stagger-step-loop-4
Outcome: The loop dispatches subagents serially through a replaceable Pi harness adapter and preserves the role boundaries.

Deliverables:
- Pi harness adapter that creates distinct role sessions and cannot mutate STEP state.
- Coordinator dispatch for initial and post-assessment ranked next-task proposals using role-specific prompt/context input.
- Worker dispatch in Docker for an approved task with inline context, path references, and structured Do/Validate output.
- Assessor dispatch for normalization, goal-progress assessment, retro, lessons, actions, and proposed next packets.
- Loop-mediated single clarification-round flow from assessor to worker and session closure when returning to a user gate.

Done when:
- The observable execution order is coordinator → worker → assessor → coordinator → user.
- Every role invocation has an isolated Pi session; only same-role follow-up work may reuse a session.
- Subagents neither invoke STEP operations nor directly message one another.
- User revisions alter only lessons and proposed-next packets before the coordinator emits a fresh YAML gate.

### PLAN-stagger-step-loop-6 — Add validation, harness, and transition tests
Closes: GAP-4, GAP-5
Source refs: REQ-010 through REQ-016, ACC-003 through ACC-006, ACC-008, ACC-009
Status: todo
Depends on: PLAN-stagger-step-loop-5
Outcome: The CLI rejects invalid packets/state and proves the approval, mediation, and Pi-harness invariants.

Deliverables:
- Packet-normalization and loop-validation test cases.
- State-transition test matrix.
- Manual-YAML-edit acceptance/rejection test cases.
- Sequencing, no-write-before-approval, and isolated-session tests.
- Mock-adapter tests and real Pi RPC server vertical-slice tests.

Done when:
- Tests cover fresh, approved, terminal, paused, revised, invalid, and blocked paths.
- Tests prove duplicate packet validation and loop state/transition validation.
- Tests prove exactly one worker clarification round, no direct subagent STEP access, and no Pi harness state mutation.
- Mock and real-server tests demonstrate the supported adapter lifecycle.
