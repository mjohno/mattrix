---
name: task
description: Use when output or map skills need the task packet contract for portable implementation context.
metadata:
  type: interface
  category: interface
---

# task

Goal: Define the minimal task packet contract for portable, self-contained implementation context.
Non-Goals: Do not draft, extract, update, implement, verify, manage whole plans, or place comments directly in files.
Use-When: Another skill needs the `task` interface contract before drafting, modifying, extracting, checking, reviewing, or stepping through a task packet.

## Selection

Default: load only the compact task contract.

Also select:
- `task_extraction.md` when the caller asks to extract a task from a plan item, annotation, spec, review finding, or prompt.
- `task_checklist.md` when the caller asks to check task conformance.
- `task_quality.md` when the caller asks to review task quality.

If caller intent is unclear, assume default contract only and state the assumption.
If requested task needs fall outside this interface, state the unsupported need and hand off to the appropriate skill.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/task_contract.md`

Optional paths:
- `references/task_extraction.md`
- `references/task_checklist.md`
- `references/task_quality.md`

## Next Steps

- `draft` — create a first-pass task packet.
- `modify` — revise a task packet while preserving stable IDs.
- `transform/check` — check task conformance with `task_checklist.md`.
- `transform/review` — review task quality with `task_quality.md`.
- `map/step` — execute one task packet.

## Minimal Example

Prompt: "Use the task interface for plan item AUTH-2."
Direct invocation response: `Loaded: references/task_contract.md.`
