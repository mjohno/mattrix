---
name: spec
description: Use when output or map skills need a future-state specification.
metadata:
  type: interface
  category: interface
---

# spec

Goal: Define the minimal future-state specification contract for traceable artifacts.
Non-Goals: Do not investigate current state, draft spec content, review correctness, create plans, make technical decisions, or implement work.
Use-When: Another skill needs the `spec` interface contract before outlining, drafting, modifying, checking, reviewing, investigating toward, or planning from a spec artifact.

## Selection

Default: load only the compact spec contract.

Also select:
- `spec_template.md` when the caller asks to outline or draft a spec.
- `spec_checklist.md` when the caller asks to check spec conformance.
- `spec_quality.md` when the caller asks to review spec quality.

If caller intent is unclear, assume default contract only and state the assumption.
If requested spec needs fall outside this interface, state the unsupported need and hand off to the appropriate skill.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/spec_contract.md`

Optional paths:
- `assets/spec_template.md`
- `references/spec_checklist.md`
- `references/spec_quality.md`

## Next Steps

- `input/investigate` — gather current-state facts and uncertainty evidence.
- `outline` — create a spec skeleton using `spec_template.md`.
- `draft` — fill the spec from source material.
- `modify` — revise a spec while preserving stable IDs.
- `output/check` — check spec conformance with `spec_checklist.md`.
- `output/review` — review spec quality with `spec_quality.md`.
- `interface/plan` — create traceable gap-closing work from spec IDs.

## Minimal Example

Prompt: "Use the spec interface for replacing the authentication module."
Direct invocation response: `Loaded: references/spec_contract.md.`
