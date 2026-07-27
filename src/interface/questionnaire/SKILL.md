---
name: questionnaire
description: Use when another skill needs the canonical questionnaire layout and question quality criteria.
metadata:
  type: interface
  category: interface
---

# questionnaire

Goal: Provide the contract shape and criteria that define good questionnaire questions.
Non-Goals: Do not execute questionnaires, discover specs or personas, produce severity reports, remediate findings, or actually define questions for a specific artifact. Discovery and question-writing are upstream tasks performed by skills that consume this interface.
Use-When: Another skill needs the questionnaire contract template and quality criteria before producing evaluation questions for an artifact.

## Selection

If caller intent is unclear, assume the default reference only.

| Reference | When |
|---|---|
| `references/questionnaire_contract.md` | Default — all cases |
| `references/questionnaire_checklist.md` | Caller asks to check contract conformance |
| `references/questionnaire_quality.md` | Caller asks to evaluate contract quality |

If requested needs fall outside this interface, state the unsupported need and hand off.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

## Next Steps

- `transform/evaluate` (execution) — evaluate the artifact against each question and answer with reasoning.
- `interface/plan` — create gap-closing work from unanswered or low-confidence questions.
- `transform/check` — validate that a revised artifact addresses prior questionnaire findings.
- `output/annotate` — add inline annotations for tracking findings (NOTE) and fixes (TODO).

## Minimal Example

**Prompt:** "Use the questionnaire interface for evaluating auth-module design against SPEC-auth using security and adversarial lenses."

**Direct invocation response:** `Loaded: references/questionnaire_contract.md.`

**Instantiated example:** `QUESTIONNAIRE-auth-module` with security + adversarial lenses, 5 questions mapped to REQ-001, REQ-003, ACC-002, ACC-003, and internal consistency.
