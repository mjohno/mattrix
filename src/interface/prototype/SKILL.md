---
name: prototype
description: Use when output or map skills need the prototype artifact contract for cheap mock-ups or validation methods.
metadata:
  type: interface
  category: interface
---

# prototype

Goal: Define the minimal prototype contract and best-fit validation profile for cheap learning.
Non-Goals: Do not build prototypes, run validation sessions, produce production implementations, or polish final deliverables.
Use-When: Another skill needs the `prototype` interface before outlining, drafting, modifying, checking, reviewing, or orchestrating a validation artifact.

## Selection

Default: load the compact prototype contract, choose the best-fit profile when possible, and retain other profiles as course-correction options in context.

Also select:
- The selected profile template when the caller asks to outline or draft a prototype.
- The selected profile quality checklist when the caller asks to check/review a prototype or validate before spending effort.

Profiles:
- `tabletop-roleplay`
- `ui-mockup`
- `process-scenario`
- `api-contract-stub`
- `data-layout-structure`

If caller intent is unclear, assume default contract only and state the assumption.
If requested prototype needs fall outside this interface, state the unsupported need and hand off to the appropriate skill.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/prototype_contract.md`

Optional paths are listed in the selected contract's profile table.

## Next Steps

- `outline` — create the prototype skeleton from the selected template.
- `draft` — fill the selected template with first-pass content.
- `modify` — revise an existing prototype while preserving selected quality criteria.
- `transform/check` — check prototype conformance against selected criteria.
- `transform/review` — review prototype quality before validation effort.

## Minimal Example

Prompt: "Use the prototype interface to validate account recovery escalation support."
Direct invocation response: `Loaded: references/prototype_contract.md.`
