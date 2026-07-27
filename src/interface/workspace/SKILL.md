---
name: workspace
description: Use when defining or applying local workspace layout conventions for Git remotes, projects, and checkouts.
metadata:
  type: interface
  category: interface
---

# workspace

Goal: Define a self-contained local workspace layout for Git remotes, projects, and checkouts.
Non-Goals: Do not define permissions, branch policy, agent workflow, backup behavior, container configuration, or repository lifecycle operations.
Use-When: Use when a task needs the canonical local layout for Git remotes, projects, or checkouts.

## Selection

Default: load the workspace layout contract.

## Context Loading

Load each selected package-local reference into context. Do not paste, quote, summarize, or otherwise reproduce its contents in chat.

When invoked alone, respond only with `Loaded: references/workspace_contract.md.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/workspace_contract.md`

## Next Steps

- `draft` — produce a workspace-specific layout proposal using this contract.
- `check` — validate a workspace layout against this contract.

## Minimal Example

Prompt: "Use the `workspace` interface for this local Git layout."
Direct invocation response: `Loaded: references/workspace_contract.md.`
