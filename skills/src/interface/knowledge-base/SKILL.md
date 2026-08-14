---
name: knowledge-base
description: Use when lookup or record needs the MKF and OKF v0.2 knowledge contract.
metadata:
  type: interface
  category: interface
  capabilities:
    - knowledge
    - mkf
    - okf
---
# knowledge-base

Goal: Define passive MKF and OKF v0.2 bundle and concept contracts for knowledge-base consumers.
Non-Goals: Do not perform lookup, resolve bundles operationally, write concepts, rebuild indexes, rank matches, or synthesize answers.
Use-When: `input/lookup`, `output/record`, or another skill needs the shared knowledge contract before reading, checking, reviewing, or writing knowledge.

## Selection

Default: load only the compact MKF contract.

Also select:
- `okf_v0_2_contract.md` when the caller needs OKF interoperability, provenance, trust, lifecycle, attested computations, cross-linking, logs, or broader OKF validation.
- `concept_frontmatter_template.md` when the caller asks to record or draft a baseline concept.
- `advanced_okf_frontmatter_template.md` when the caller explicitly asks to author advanced OKF metadata.
- `knowledge_checklist.md` when the caller asks to check conformance.
- `knowledge_quality.md` when the caller asks to review knowledge quality.

If caller intent is unclear, assume the MKF contract only and state the assumption. If requested work falls outside this interface, state the unsupported need and hand off to `input/lookup` or `output/record`.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/mkf_contract.md`

Optional paths:
- `references/okf_v0_2_contract.md`
- `assets/concept_frontmatter_template.md`
- `assets/advanced_okf_frontmatter_template.md`
- `references/knowledge_checklist.md`
- `references/knowledge_quality.md`

## Next Steps

- `input/lookup` — resolve bundles, search concepts, and load selected concepts.
- `output/record` — create or update concepts and explicitly rebuild indexes when requested.
- `output/check` — check conformance with `knowledge_checklist.md`.
- `output/review` — review quality with `knowledge_quality.md`.

## Minimal Example

Prompt: "Use the knowledge-base interface before recording a concept."
Direct invocation response: `Loaded: references/mkf_contract.md.`
