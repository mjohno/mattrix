---
name: flow
description: Use when work needs a process-flow diagram with typed nodes, transition criteria, and plain-language descriptions.
metadata:
  type: interface
  category: interface
---

# flow

Goal: Define a compact process-flow artifact with typed nodes, allowed transitions, and testable transition criteria.

Non-Goals: Do not select tasks or workers, execute work, store state, or enforce transitions.

Use-When: Use when a user needs to describe, draft, review, or follow a visible process flow with activities, decisions, rework paths, and completion criteria.

## Selection

Default: load `references/flow_contract.md`.

Also select:
- `references/flow_quality.md` when the user asks to check, review, or improve a flow.

## Context Loading

Load each selected package-local reference into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/flow_contract.md`

Optional path:
- `references/flow_quality.md`

## Next Steps

- `outline` — create a flow structure.
- `draft` — create a first-pass flow.
- `modify` — change a flow.
- `check` — validate a flow.
- `decide` — suggest a next step that follows a flow.

## Minimal Example

Prompt: "Use the `flow` interface to draft a delivery workflow."
Direct invocation response: `Loaded: references/flow_contract.md.`
