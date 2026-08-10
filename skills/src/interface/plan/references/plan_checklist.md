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
