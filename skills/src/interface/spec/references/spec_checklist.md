# Spec Checklist

Use this for conformance checks. A spec passes when every critical item passes.

## Critical

- [ ] Has a title and stable `SPEC-<slug>` ID.
- [ ] Includes Purpose, Current State Summary, Future State, Scope, Requirements, Acceptance, Quality, Expectations, Uncertainties, and Decisions.
- [ ] Referenceable claims use stable IDs.
- [ ] Scope includes both `In Scope` and `Out of Scope`.
- [ ] Quality includes both `Constraints / Non-Negotiables` and `Priorities`.
- [ ] Uncertainties includes `Risks`, `Questions`, `Assumptions`, and `Pre-Work Needed`.
- [ ] The artifact defines a future state, not an implementation plan.

## Optional but Checkable

- [ ] Acceptance criteria are observable, reviewable, or measurable.
- [ ] Decisions include status and rationale where useful.
- [ ] Plan items can trace to relevant spec IDs without copying full spec text.

## Quality

A failed Quality item produces a `Partial` result. It does not fail conformance.

- [ ] The spec explains why it exists without prematurely planning implementation.
- [ ] Current-state claims are separate from assumptions.
- [ ] The future state is concrete enough for a plan to target.
- [ ] In-scope and out-of-scope boundaries are clear.
- [ ] Requirements are testable, reviewable, or otherwise judgeable.
- [ ] Requirements do not duplicate scope or acceptance criteria.
- [ ] Acceptance defines observable judgment signals.
- [ ] Acceptance does not prematurely mandate implementation artifacts.
- [ ] Constraints are separate from priorities.
- [ ] Risks, questions, assumptions, and pre-work are visibly separate.
- [ ] Settled decisions are distinct from assumptions and open questions.
- [ ] Downstream work can trace to stable IDs without copying large sections.
