---
name: coordinate
description: Orchestrate end-to-end local work by maintaining coordinates, choosing next steps, delegating when useful, and reconciling progress. Use when local work needs coordination across skills, artifacts, files, or sub-agents.
metadata:
  type: skill
  category: map
---

# coordinate

Goal: Orchestrate local work toward a goal by maintaining coordination state, selecting next steps, using appropriate skills, delegating independent work when useful, reconciling results, and stopping when blocked or complete.
Non-Goals: Do not act as a persona, define artifact schemas, replace `spec`/`plan`/`task`/`check`/`review`, create a universal lifecycle, deploy, release, publish, promote, or coordinate remote environment changes.
Use-When: Local work needs end-to-end orchestration across multiple steps, artifacts, files, checks, reviews, or sub-agents.

## 0. Prerequisites

- A local goal, target, change ID, plan, task, issue, or other reference to coordinate from.
- If invoked with a change ID, use the `change` interface contract and the workspace at `./tmp/changes/<change-id>/`.
- If no change ID is supplied, keep coordinates in prompt context only.
- One active change at a time when coordinating a change.

## 1. Inputs

- Goal or desired outcome.
- Current position, references, artifacts, files, plans, tasks, findings, or user constraints.
- Optional change ID.
- Optional stop conditions, approval boundaries, or delegation constraints.

## 2. Coordinate State

Coordinate state is called `coords`.

### Prompt-only mode

Use prompt-only mode when no change ID is supplied.

- Maintain coords in the conversation context.
- Do not create `COORDS.md`.
- Do not create a change workspace unless the user asks or the `change` trigger rules clearly apply.

### Change-scoped mode

Use change-scoped mode only when invoked with a change ID.

- Read and update `./tmp/changes/<change-id>/COORDS.md`.
- Create `COORDS.md` if it does not exist.
- Respect the `change` contract: one active change, prompt/context active selection only, temporary local files, and no deployment/release scope.
- Do not create `COORDS.md` merely because a change directory exists.

### COORDS.md shape

Use `assets/coords_template.md` when creating `COORDS.md`.

## 3. Processes

1. **Orient**: Identify the goal, active change if any, current position, known context, constraints, and stop conditions.
2. **Locate gaps**: Determine what is missing or uncertain between current position and target outcome.
3. **Choose next move**: Select the smallest useful next step. Use existing artifact skills when artifact structure matters:
   - `spec` for desired future state.
   - `plan` for ordered gap-closing work.
   - `task` for portable implementation context.
   - `check` for validation against criteria.
   - `review` for evaluation findings.
4. **Execute or delegate**: Do direct local work when the step is clear; delegate independent work when it is meaningfully separable.
5. **Reconcile**: Read sub-agent results or produced artifacts, compare them against the goal and constraints, resolve conflicts, and identify remaining gaps.
6. **Update coords**: Record current position, decisions, open questions, delegations, next step, and stop conditions in prompt context or `COORDS.md`.
7. **Report**: Briefly report progress, evidence, current state, and the next recommended step.
8. **Stop when needed**: Stop and ask the user when blocked by missing decisions, meaningful ambiguity, approval boundaries, risky changes, or out-of-scope deployment/release requests.

## 4. Delegation Rules

Delegate only when useful for independent work, such as:

- investigation with bounded scope
- review from a distinct perspective or against criteria
- checking an artifact or result
- implementation work that can be isolated and verified

Delegation prompts must include:

- goal and local scope
- exact inputs or references
- expected output
- whether file changes are allowed
- constraints and stop conditions

After delegation:

- Reconcile results before advancing.
- Verify changed files or claims when practical.
- Do not treat a sub-agent summary as proof without checking important artifacts or evidence.
- Do not duplicate delegated exploration unless needed for verification or conflict resolution.

## 5. Outputs

- Updated coords in prompt context, or in `./tmp/changes/<change-id>/COORDS.md` when change-scoped.
- Brief coordination report with current position, completed moves, evidence, open questions, and next step.
- Local artifacts created by downstream skills or direct work, rooted in the change directory when change-scoped.

## 6. Next Steps

- `change` — create or check a temporary local change workspace contract.
- `draft` with `spec` — draft a future-state specification when target state is unclear.
- `draft` with `plan` — draft ordered gap-closing work when sequencing is unclear.
- `step` — execute one explicit step with verification and human review.
- `check` — validate an object, result, or artifact against criteria.
- `review` — evaluate an artifact or result using review criteria or personas.

## 7. Examples

### Example 1: Prompt-only coordination

**Prompt:** Coordinate the next steps for cleaning up the parser tests.
**Outcome:** Maintains coords in the chat, identifies missing context, proposes or executes the next local step, and reports progress without creating `COORDS.md`.

### Example 2: Change-scoped coordination

**Prompt:** Coordinate change `auth-error-cleanup`.
**Outcome:** Uses `./tmp/changes/auth-error-cleanup/COORDS.md`, updates current position and next step, delegates independent checks if useful, reconciles results, and stops before any deployment or release work.
