---
name: change
description: Use when output or map skills need the temporary local change workspace contract.
metadata:
  type: interface
  category: interface
---

# change

Goal: Define the minimal temporary local workspace contract for work that concerns a target plus an intended or possible delta.
Non-Goals: Do not coordinate work, define a lifecycle, draft specs/plans/tasks/checks/reviews, implement changes, deploy, release, or create repository-level active-change state.
Use-When: Another skill needs the `change` interface contract before creating, using, checking, or coordinating temporary local change workspace artifacts.

## Selection

Default: load only the compact change contract.

Also select:
- `change_template.md` when the caller asks to create, scaffold, outline, or draft a `CHANGE.md` file.
- `change_checklist.md` when the caller asks to check change workspace conformance or skill compliance.

If caller intent is unclear, assume default contract only and state the assumption.
If requested change needs fall outside this interface, state the unsupported need and hand off to the appropriate skill.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/change_contract.md`

Optional paths:
- `assets/change_template.md`
- `references/change_checklist.md`

## Next Steps

- `draft` — create a first-pass `CHANGE.md` from the template.
- `modify` — revise an existing change workspace artifact while preserving boundaries.
- `output/check` — check change workspace conformance with `change_checklist.md`.
- `map/coordinate` — orchestrate local work using prompt coordinates or change-scoped `COORDS.md`.

## Minimal Example

Prompt: "Use the change interface for auth error cleanup."
Direct invocation response: `Loaded: references/change_contract.md.`
