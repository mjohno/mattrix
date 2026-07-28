---
name: knowledge-base
description: Use when lookup or record needs the passive MKF contract.
metadata:
  type: interface
  category: interface
  capabilities:
    - knowledge
    - mkf
---
# knowledge-base

Goal: Define the passive MKF concept, bundle, and manual discovery contract for knowledge-base consumers.
Non-Goals: Do not perform lookup, resolve bundles operationally, write concepts, rebuild indexes, rank matches, or synthesize answers.
Use-When: `input/lookup`, `output/record`, or another skill needs the shared MKF contract before reading, checking, reviewing, or writing knowledge.

## Selection

Default: load only the compact knowledge-base contract.

Also select:
- `concept_frontmatter_template.md` when the caller asks to record or draft a concept.
- `knowledge_checklist.md` when the caller asks to check MKF conformance.
- `knowledge_quality.md` when the caller asks to review MKF quality.

If caller intent is unclear, assume default contract only and state the assumption.
If requested knowledge-base work falls outside this interface, state the unsupported need and hand off to `input/lookup` or `output/record`.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/knowledge_contract.md`

Optional paths:
- `assets/concept_frontmatter_template.md`
- `references/knowledge_checklist.md`
- `references/knowledge_quality.md`

## Next Steps

- `input/lookup` — resolve bundles operationally, search MKF metadata, and load selected concepts.
- `output/record` — create or update MKF concepts and rebuild generated indexes.
- `output/check` — check MKF conformance with `knowledge_checklist.md`.
- `output/review` — review MKF quality with `knowledge_quality.md`.

## Minimal Example

Prompt: "Use the knowledge-base interface before recording a new concept."
Direct invocation response: `Loaded: references/knowledge_contract.md.`
