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
Outcome: <artifact, decision, or state>

Deliverables:
- <deliverable>

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
- Plan items are not task packets; full task packets stay external.

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
Outcome: Consistent login error copy and recovery guidance.

Deliverables:
- Updated login error message table.

Done when:
- Each login failure mode maps to one approved user-facing message.
```
