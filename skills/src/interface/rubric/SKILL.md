---
name: rubric
description: Use when another skill needs a concise, referenceable quality rubric.
metadata:
  type: interface
  category: interface
---

# rubric

Goal: Define a concise, reusable quality rubric with referenceable criteria.
Non-Goals: Do not apply criteria, record results, collect evidence, define follow-up work, make completion decisions, or implement work.
Use-When: Another skill needs a quality standard before outlining, drafting, modifying, checking, reviewing, or consuming a rubric artifact.

## Selection

Default: load only the compact rubric contract.

Also select:
- `assets/rubric_template.md` when the caller asks to outline or draft a rubric.
- `references/rubric_checklist.md` when the caller asks to check rubric conformance or review rubric quality.

If caller intent is unclear, assume default contract only and state the assumption.
If the requested need falls outside this interface, state the unsupported need and hand off.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/rubric_contract.md`

Optional paths:
- `assets/rubric_template.md`
- `references/rubric_checklist.md`

## Next Steps

- `draft` — create a first-pass rubric from supplied context.
- `modify` — revise a rubric while preserving stable criterion IDs.
- `output/check` — check a rubric or target against rubric criteria.
- `output/review` — review an artifact using a rubric as the criteria source.

## Minimal Example

Prompt: "Use the rubric interface to draft a quality rubric for the auth module."
Direct invocation response: `Loaded: references/rubric_contract.md.`
