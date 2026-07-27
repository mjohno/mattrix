---
name: goal
description: Use when output skills need a SMART goal contract, template, or checklist.
metadata:
  type: interface
  category: interface
---

# goal

Goal: Define the minimal SMART goal contract for a clear, assessable intended outcome.
Non-Goals: Do not elicit goals, choose priorities, draft goal content, execute work, or evaluate achievement.
Use-When: Another skill needs the `goal` interface contract before drafting, modifying, checking, or reviewing a goal.

## Selection

Default: load only the compact SMART goal contract.

Also select:
- `goal_template.md` when the caller asks to outline or draft a goal.
- `goal_checklist.md` when the caller asks to check goal conformance or completeness.

If caller intent is unclear, assume the default contract only and state the assumption.
If the requested need falls outside this interface, state the unsupported need and hand off to the appropriate skill.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/goal_contract.md`

Optional paths:
- `assets/goal_template.md`
- `references/goal_checklist.md`

## Next Steps

- `draft` — create a first-pass goal from supplied context.
- `modify` — revise an existing goal while preserving its intended outcome.
- `output/check` — check a goal against `goal_checklist.md`.
- `output/review` — review goal clarity and feasibility.
- `map/step` — turn an approved goal into recorded, user-gated next-best-step progress.

## Minimal Example

Prompt: "Use the goal interface to draft a goal for reducing response times."
Direct invocation response: `Loaded: references/goal_contract.md.`
