# Plan Checklist

Use this for conformance checks. A plan passes when every critical item passes.

## Critical

- [ ] Defines a plan artifact, not an execution log or spec.
- [ ] Includes `PLAN_ID`, `Source`, `Purpose`, `Source Summary`, `Gap Map`, and `Work Plan`.
- [ ] Source Summary contains enough context to review the plan without reloading the full source.
- [ ] Every gap has a stable `GAP-*` ID.
- [ ] Every gap states a current problem and target state.
- [ ] Every gap has at least one work item intended to close it.
- [ ] Every work item has a stable item ID, title, `Closes`, `Status`, one `Task`, and a `Scenarios` declaration.
- [ ] Scenario IDs are stable and unique within the plan; each scenario uses semantic Gherkin, or the work item explicitly states `Scenarios: none`.
- [ ] Every work item names the gap or source it serves.
- [ ] Status values are limited to `todo`, `doing`, `verifying`, `reviewing`, or `done`.
- [ ] `done` is not presented as verification evidence.
- [ ] Every `Task` is one bounded INVEST paragraph, does not duplicate `Deliverables` or `Done when`, and retains plan metadata.

## Optional but Checkable

- [ ] Dependencies are present where sequencing matters.
- [ ] Deliverables are present where the expected artifact/output could be ambiguous.
- [ ] Done criteria are present where completion boundaries could be ambiguous.

## Quality

A failed Quality item produces a `Partial` result. It does not fail conformance.

- [ ] The plan is readable end to end without loading the full source artifact.
- [ ] Gaps are real differences between the current problem and target state.
- [ ] The work plan makes the path to the target state obvious.
- [ ] Items are split at useful boundaries without becoming tiny checklist fragments.
- [ ] Related gaps are grouped when coupling is real and separated when work can proceed independently.
- [ ] IDs are stable, traceable, and easy to reference in follow-up work.
- [ ] Dependencies, deliverables, and done criteria are included only where they reduce ambiguity.
- [ ] The plan does not present status as execution evidence.
- [ ] Each task statement is a concise, bounded paragraph that improves implementation readiness.
- [ ] Each scenario describes a meaningful vertical behavior from a relevant starting state through an action or event to an observable outcome.
- [ ] Scenarios avoid combinatorial input matrices, lower-level invariants, and edge-case catalogues that are not distinct, meaningful plan behaviors.
- [ ] The plan is concise enough to maintain, review, and update.
