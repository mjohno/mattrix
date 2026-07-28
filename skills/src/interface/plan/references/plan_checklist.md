# Plan Checklist

Use this for conformance checks. A plan passes when every critical item passes.

## Critical

- [ ] Defines a plan artifact, not an execution log, task packet, or spec.
- [ ] Includes `PLAN_ID`, `Source`, `Purpose`, `Source Summary`, `Gap Map`, and `Work Plan`.
- [ ] Source Summary contains enough context to review the plan without reloading the full source.
- [ ] Every gap has a stable `GAP-*` ID.
- [ ] Every gap states a current problem and target state.
- [ ] Every gap has at least one work item intended to close it.
- [ ] Every work item has a stable item ID, title, `Closes`, `Status`, and `Outcome`.
- [ ] Every work item names the gap or source it serves.
- [ ] Status values are limited to `todo`, `doing`, `verifying`, `reviewing`, or `done`.
- [ ] `done` is not presented as verification evidence.
- [ ] Full task packets are external, not embedded in the plan.

## Optional but Checkable

- [ ] Dependencies are present where sequencing matters.
- [ ] Deliverables are present where the expected artifact/output could be ambiguous.
- [ ] Done criteria are present where completion boundaries could be ambiguous.
