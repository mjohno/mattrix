---
name: delegate
description: Use when work needs a task or full handoff performed by a fresh subagent, optionally through a persona.
metadata:
  type: skill
  category: map
---

# delegate

Goal: Delegate work to a fresh subagent with either focused task context or a full handoff.
Non-Goals: Do not perform the delegated work, invent missing context, persist delegation state unless requested, or approve the returned result.
Use-When: Use when a fresh subagent should perform a task or continue a branch of work.

## 0. Prerequisites

- Work to delegate.
- Relevant current context or a clear request for missing material.
- An available subagent invocation mechanism.
- `handoff` when the delegation mode is `handoff`.
- `interface/change` when a handoff uses a caller-supplied change path.

## 1. Inputs

- Delegation mode:
  - `task` for one specific task.
  - `handoff` for continued ownership of a branch of work.
- Delegated action, such as `implement`, `review`, `investigate`, or `draft`.
- Optional persona skill, such as `architect`, `security`, or `tester`.
- Current goal, relevant artifacts, facts, constraints, decisions, and acceptance criteria.
- Required result format, scope, isolation, and permissions, when supplied.
- A suitable available subagent agent definition or plugin.
- `references/delegation_quality.md` when the user asks to check, review, or improve a delegation.

## 2. Processes

1. Select the delegation mode:
   - Use `handoff` when the delegation prompt contains the `handoff` keyword, including when it also contains `task`.
   - Otherwise, use `task` when the delegation prompt contains the `task` keyword.
   - Otherwise, infer the smallest suitable mode:
     - Use `task` for one specific action with focused context.
     - Use `handoff` when a fresh subagent must continue a branch of work from the current state.
2. Identify the delegated action, optional persona, required result, scope, isolation, and permissions.
3. Select a suitable available subagent agent definition or plugin. Use a caller-selected agent when supplied; otherwise match its description and permissions to the work, then use a safe general-purpose fallback.
4. For `task` mode:
   - Select only the context required for the specific task.
   - Build a short, self-contained task prompt.
5. For `handoff` mode:
   - When the caller supplies a change path, load and apply `interface/change` before `handoff`.
   - Use the `handoff` skill to create a concrete handoff for the delegated branch of work.
   - Pass the handoff inline unless the caller supplies a change path.
   - Use the handoff as the primary context for the fresh subagent.
   - Add only invocation details not contained in the handoff, such as the selected agent, isolation, permissions, and required return format.
6. If a persona is supplied, instruct the subagent to load and apply that persona skill. Do not copy persona instructions into the delegation prompt.
7. Return a clarification request or blocked result when no suitable agent, required context, invocation mechanism, or named persona is available.
8. Invoke the subagent without inherited conversation context.
9. Return the subagent result, evidence, assumptions, and uncertainties. Do not approve the result.

## 3. Outputs

- In `task` mode, one subagent result for the specific task.
- In `handoff` mode:
  - One concrete handoff, passed inline or written to the supplied change path.
  - One subagent result for the continued branch of work.
- A blocked result when required context, a persona, an agent, or an invocation mechanism is unavailable.
- The generated task prompt or handoff when the caller requests it.

## 4. Next Steps

- `check` — validate the subagent result.
- `decide` — suggest the next action from the result.
- `delegate task` — delegate a separate specific task.
- `delegate handoff` — transfer another branch of work.
- `flow` — apply the result to a workflow.

## 5. Examples

### Example 1: Explicit task

**Prompt:** `/skill:delegate task review the current diff with the security persona`

**Outcome:** Creates a focused task prompt, invokes a suitable fresh subagent, and instructs it to load and apply `security` before the review.

### Example 2: Explicit inline handoff

**Prompt:** `/skill:delegate handoff continue the validation implementation with the ponytail persona`

**Outcome:** Uses `handoff` to create an inline continuation document, invokes a suitable fresh subagent, and instructs it to load and apply `ponytail` before continuing the work.

### Example 3: Inferred task

**Prompt:** `/skill:delegate investigate why this test fails`

**Outcome:** Infers `task` because the request is one specific action with focused context.

### Example 4: Inferred handoff

**Prompt:** `/skill:delegate have a fresh implementer continue the authentication branch from the current state with the architect persona`

**Outcome:** Infers `handoff` because the subagent must continue a branch of work from the current state, creates an inline handoff, and instructs the fresh subagent to load and apply `architect`.
