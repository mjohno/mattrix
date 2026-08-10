# Plan Contract

A plan is a gap-closing artifact: it explains how work moves from a current problem state to a target state.

## Required Shape

```text
# Plan: <title>

PLAN_ID: <stable-id>
Source: <source artifact, prompt, or context>
Purpose: <target outcome>

## Source Summary
- <source ref/topic>: <short summary needed to review the plan>

## Gap Map
| Gap ID | Source Summary | Current Problem | Target State |
| --- | --- | --- | --- |
| GAP-1 | <source ref/topic> | <problem> | <target> |

## Work Plan

### <PLAN_ID>-1 — <item title>
Closes: GAP-1
Source refs: <refs/topics or none>
Status: todo
Depends on: none
Task: <one bounded INVEST paragraph; use the `task` skill to draft it>

Deliverables:
- <deliverable>

Scenarios:
- SCN-<PLAN_ID>-<N>: <short behavioural name>
  Given <relevant starting state>
  When <meaningful action or event>
  Then <observable outcome>

Done when:
- <condition>
```

## Contract Rules

- Prefer gap closure over checklist phrasing.
- Include enough source summary to review the plan without reloading the full source artifact.
- Every gap has at least one closing item.
- Every item names the gap or source it serves.
- Preserve stable gap and item IDs across revisions unless explicitly renamed.
- Items may close multiple gaps when the coupling is real.
- Dependencies, deliverables, and done criteria are included when they reduce ambiguity.
- Every work item includes one bounded `Task` paragraph that states the intended outcome without duplicating `Deliverables`, `Scenarios`, or `Done when`.
- Every work item includes `Scenarios`. Use one or more scenarios when the item establishes, preserves, or removes distinct observable behaviour. Otherwise, state `Scenarios: none`.
- Scenario IDs are stable and unique within a plan. Change an ID only when its behaviour is removed or materially split.
- Write scenarios with semantic Gherkin: `Given`, `When`, `Then`, and, when necessary, `And` or `But`.
- Each scenario describes one meaningful vertical behaviour from a relevant starting state through an action or event to an observable outcome.
- Do not use scenarios for combinatorial input matrices, lower-level invariants, or edge-case catalogues unless they are distinct behaviours meaningful to the plan.
- Do not prescribe implementation, tools, test frameworks, or verification methods in scenarios.
- Use the `task` skill (or `/skill:task`, if available) to draft or refine each `Task` against its INVEST quality criteria, then retain the item's plan metadata.

## Status Values

Use only:

- `todo`
- `doing`
- `verifying`
- `reviewing`
- `done`

`done` means the plan artifact says the item is no longer planned work. It is not verification evidence by itself.

## Minimal Example

```text
# Plan: Login Error Cleanup

PLAN_ID: PLAN-login-errors
Source: Auth review findings
Purpose: Make login failures clear and actionable.

## Source Summary
- Auth review: Login errors are inconsistent and hide actionable recovery steps.

## Gap Map
| Gap ID | Source Summary | Current Problem | Target State |
| --- | --- | --- | --- |
| GAP-1 | Auth review: inconsistent errors | Users see vague or conflicting login errors. | Login failures use clear, consistent recovery guidance. |

## Work Plan

### PLAN-login-errors-1 — Normalize login failure messages
Closes: GAP-1
Source refs: Auth review
Status: todo
Depends on: none
Task: Normalize login failure messages so users receive clear, consistent recovery guidance and the product avoids conflicting error copy. Preserve existing error-code behavior.

Deliverables:
- Updated login error message table.

Scenarios:
- SCN-PLAN-login-errors-1: Invalid credentials return recovery guidance
  Given a user attempts to sign in to an existing account
  When authentication fails because the credentials are invalid
  Then the user receives the approved invalid-credentials message
  And the existing authentication error code is preserved

Done when:
- Each login failure mode maps to one approved user-facing message.
```
