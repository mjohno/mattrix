---
name: delegate
description: Use when current work needs one bounded action performed by an isolated subagent, optionally through a persona.
metadata:
  type: skill
  category: map
---

# delegate

Goal: Delegate one bounded action to a subagent with the context it needs.
Non-Goals: Do not perform the delegated action, invent missing context, persist delegation state, or approve the returned result.
Use-When: Use when a subagent should perform an action from current context, optionally using a named persona.

## 0. Prerequisites

- A delegated action.
- Relevant current context or a clear request for missing material.
- An available subagent invocation mechanism.

## 1. Inputs

- Delegated action, such as `review`, `investigate`, or `draft`.
- Optional persona, such as `security` or `adversarial`.
- Current goal, relevant artifacts, facts, constraints, and acceptance criteria.
- Required result format, scope, and permissions, when supplied.
- A suitable available subagent agent definition or plugin.
- `references/delegation_quality.md` when the user asks to check, review, or improve a delegation.

## 2. Processes

1. Identify the delegated action, optional persona, required result, and scope.
2. Select only material that the subagent needs. Do not pass unrelated conversation context.
3. Select a suitable available subagent agent definition or plugin. Use a caller-selected agent when supplied; otherwise match its description to the action, then use a safe general-purpose fallback.
4. Return a clarification request or blocked result when no suitable agent, required context, or named persona is available.
5. Build a self-contained task prompt for the isolated subagent.
6. If a persona is supplied, instruct the subagent to load and apply that persona skill. Do not copy persona instructions into the task prompt.
7. Invoke the subagent and return its result, evidence, assumptions, and uncertainties.

## 3. Outputs

- One subagent result for the delegated action.
- A blocked result when required context, a persona, or an invocation mechanism is unavailable.
- The generated task prompt when the caller requests it.

## 4. Next Steps

- `check` — validate the subagent result.
- `decide` — suggest the next action from the result.
- `delegate` — delegate a separate bounded action.
- `flow` — apply the result to a workflow.

## 5. Examples

### Example 1

**Prompt:** `/skill:delegate review to security`

**Outcome:** Invokes a suitable isolated subagent to review the relevant current artifact. The subagent loads and applies the `security` persona. It returns its findings, evidence, assumptions, and uncertainties.
