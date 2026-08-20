---
name: assessment
description: Use when another skill needs the canonical assessment layout, category catalog, and question-result criteria.
metadata:
  type: interface
  category: interface
---

# assessment

Goal: Provide the contract shape and criteria for a scoped, category-based assessment.
Non-Goals: Do not execute assessments, discover target resources or criteria, define domain-specific questions, produce severity reports, remediate findings, make completion decisions, or implement work.
Use-When: Another skill needs the assessment contract, template, or checklist before creating, checking, reviewing, or consuming an assessment.

## Selection

If caller intent is unclear, assume the default reference only.

| Reference | When |
|---|---|
| `references/assessment_contract.md` | Default — all cases |
| `assets/assessment_template.md` | Caller asks to outline or draft an assessment |
| `references/assessment_checklist.md` | Caller asks to check assessment conformance or review assessment quality |

If requested needs fall outside this interface, state the unsupported need and hand off.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

## Next Steps

- `output/check` — validate an assessment or its target against assessment questions and report the status of each question.
- `output/review` — use an assessment or its checklist as the criteria source for a structured review.
- `interface/plan` — create gap-closing work from partial, failed, or insufficient-evidence answers.
- `output/annotate` — add inline annotations for tracking findings and fixes.

## Minimal Example

**Prompt:** "Use the assessment interface to draft an assessment of the auth module."

**Direct invocation response:** `Loaded: references/assessment_contract.md.`

**Instantiated example:** `ASSESSMENT-auth-module` scopes the auth-module resources and asks relevant Correctness and Security questions with evidence-backed answers.
