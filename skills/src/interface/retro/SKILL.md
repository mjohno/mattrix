---
name: retro
description: Use when output or map skills need the markdown contract for a current-session retrospective with wins, issues, and actions.
metadata:
  type: interface
  category: interface
---

# retro

Goal: Define a concise markdown retrospective contract for recording the wins, issues, and actions of a current session.
Non-Goals: Do not conduct a retrospective, investigate evidence, assign actions, track work, or write tasks.
Use-When: Another skill needs the `retro` interface before outlining, drafting, modifying, checking, or reviewing a current-session retrospective.

## Selection

Default: load only the compact retro contract.

Also select:
- `retro_template.md` when the caller asks to outline, draft, or modify a retro file.
- `retro_checklist.md` when the caller asks to check retro conformance or review retro quality.

If the session scope is unclear, retain it as an explicit uncertainty. If the requested artifact is not a current-session retrospective, state the unsupported need and hand off to the appropriate skill.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/retro_contract.md`

Optional paths:
- `assets/retro_template.md`
- `references/retro_checklist.md`

## Next Steps

- `outline` — create a retro skeleton from the selected template.
- `draft` — create a first-pass retro from supplied session context.
- `modify` — revise a retro while preserving supported session evidence.
- `task` — turn an action into a concise INVEST task statement.
- `output/check` — check retro conformance and quality with `retro_checklist.md`.
- `output/review` — review retro quality with `retro_checklist.md`.

## Minimal Example

Prompt: "Use the retro interface to draft a retrospective for this session."
Direct invocation response: `Loaded: references/retro_contract.md.`
