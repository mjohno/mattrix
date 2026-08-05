---
name: change
description: Use when another skill needs the local artifact-directory contract for a caller-provided change path.
metadata:
  type: interface
  category: interface
---

# change

Goal: Define the minimal local artifact-directory contract for a supplied change path.
Non-Goals: Do not select, create, identify, or coordinate a change; define a lifecycle; draft artifacts; implement work; deploy; release; or create persistent state.
Use-When: Another skill receives a change path and needs the `change` interface contract before using or checking change-scoped local artifacts.

## Selection

Default: load only the compact change-path contract.

Also select:
- `change_checklist.md` when the caller asks to check change-path conformance or interface compliance.

If caller intent is unclear, assume default contract only and state the assumption.
If the caller has not supplied a change path, ask the caller to supply the path; the interface has no artifact location to govern.

## Context Loading

Load each selected package-local reference into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/change_contract.md`

Optional paths:
- `references/change_checklist.md`

## Next Steps

- `modify` — revise a change-scoped artifact while preserving its own contract.
- `output/check` — check artifact-location conformance with `change_checklist.md`.

## Minimal Example

Prompt: "Use the change interface for artifacts at the supplied change path."
Direct invocation response: `Loaded: references/change_contract.md.`
