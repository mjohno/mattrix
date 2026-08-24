---
name: rfc
description: Use when a request for comment needs independent lens-based review, assessed findings, and governed follow-up.
metadata:
  type: protocol
  category: map
---

# rfc

Goal: Govern an RFC from scoped independent review through finding assessment, follow-up, validation, and closure.
Non-Goals: Implementing annotated fixes, discovering criteria or lenses, reviewing unspecified sources, or changing sources without approval.
Use-When: The user explicitly asks to run RFC, rfc, or request-for-comment feedback.

## 0. Prerequisites
- Explicit sources or pasted content, criteria, and at least one reviewer lens
- A change path (`interface/change` skill) when a persistent RFC document is required; otherwise, use the prompt as the RFC record
- Permission to edit each named source when an Annotate action is selected
- `output/review`, `output/annotate`, `output/check`, and `interface/plan` available when their stages apply

## 1. Protocol Interface
- Authoritative interface: `RFC-<slug>.md` at the supplied change root, using [assets/rfc_template.md](assets/rfc_template.md); without a change root, the prompt record is authoritative.
- Primary stages: Scope, Create RFC, Blind Review, Merge, Assess, Action, Validate, Close.
- The coordinator reads the interface to derive ready tasks. All role results, dispositions, action evidence, and validation results are recorded there.
- `use_subagents` is false by default. When explicitly true, one clean subagent performs each source/lens Blind Review.

## 2. Invariants
- A source/lens review is blind: before it finishes, its reviewer must not read the RFC record, prior reports, findings, assessments, actions, or validation results.
- A blind reviewer receives only its source, resolved criteria, lens, and `output/review` report format. It must not edit a source or the RFC record.
- Only the serialized Merge stage reads both an independent review result and the current RFC record. It preserves each report, adds new findings, links duplicates, and adds insights to related findings.
- Each finding has a stable ID, one lifecycle status (`Open`, `Assessed`, `Actioning`, `Validating`, or `Closed`), and one disposition: `Accept`, `Annotate`, or `Plan`.
- `Accept` records a decision-maker and no-action rationale, then closes the finding. It creates no source change.
- `Annotate` uses `output/annotate`; a corrective annotation uses the formal `FIX` kind. `Plan` uses `draft` with `interface/plan`.
- Annotate and Plan results require `output/check` against their declared criteria. A failed check returns only to the related Action stage.
- Close only when every scoped source/lens review is complete and every finding is closed. Do not mutate protocol state outside the authoritative interface.

## 3. Outputs
- An RFC record in the supplied change root (`interface/change` skill), or an equivalent prompt record
- Embedded independent review reports, a merged finding register, dispositions, action evidence, and validation results
- Inline annotations or plan artifacts only for findings routed to those actions
- A closure decision with the decision-maker and unresolved risks or deferred decisions

## 4. Next Steps
- `modify` — perform a selected `FIX` or `TODO` annotation as a separate task
- `output/review` — re-review an action result when the RFC requires additional evidence

## 5. Examples

### Example 1

**Prompt:** "Run RFC for the supplied change path on `docs/auth.md` with security and system-architect lenses. Use subagents."
**Outcome:** The protocol creates `RFC-auth.md`, runs clean independent reviews, merges the reports, assesses every finding, validates routed annotations or plans, and closes only resolved findings.
