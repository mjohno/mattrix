---
name: values
description: Use when another skill needs a standalone values profile to guide decision priorities.
metadata:
  type: interface
  category: interface
---

# values

Goal: Define a compact, standalone values-profile contract for guiding decision priorities.
Non-Goals: Do not select a profile by default, make decisions, apply priorities, draft profile content, review results, or execute work.
Use-When: Another skill needs the `values` interface contract before outlining, drafting, modifying, checking, reviewing, or using a values-profile artifact.

## Selection

Default: load only the compact values-profile contract.

Also select:
- `values_template.md` when the caller asks to outline or draft a values profile.
- `values_checklist.md` when the caller asks to check values-profile conformance or review values-profile quality.

A values profile is used only when the caller explicitly names it. If no profile is named, the consuming skill continues without values-specific guidance.

If caller intent is unclear, assume default contract only and state the assumption.
If requested values-profile needs fall outside this interface, state the unsupported need and hand off to the appropriate skill.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/values_contract.md`

Optional paths:
- `assets/values_template.md`
- `references/values_checklist.md`

## Next Steps

- `outline` — create a values-profile structure using `values_template.md`.
- `draft` — create a first-pass values profile from supplied context.
- `modify` — revise a values profile while preserving its stable ID.
- `output/check` — check values-profile conformance and quality with `values_checklist.md`.
- `output/review` — review a values profile with `values_checklist.md`.
- `output/decide` — suggest one decision using an explicitly named values profile.

## Minimal Example

Prompt: "Use the values interface to draft a product values profile."
Direct invocation response: `Loaded: references/values_contract.md.`
