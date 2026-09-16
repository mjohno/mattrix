---
name: reflect
description: Route current-session learning from an existing retro into approved, scoped short-term and long-term knowledge updates.
metadata:
  type: skill
  category: map
---

# reflect

Goal: Route current-session learning from an existing retro into approved, scoped short-term and long-term knowledge updates.
Non-Goals: Do not create a retro, invent lessons, write unapproved updates, or update skill packages.
Use-When: A user invokes `/reflect` after a current-session retro exists and wants reviewable learning proposals or approved persistence.

## 0. Prerequisites

- A current-session retro with Session, Goal, Evidence, Wins, Issues, and Actions.
- User-approved targets before persistence.
- An unambiguous MKF bundle path before long-term-memory persistence.

## 1. Inputs

- Current-session retro.
- Optional target paths or MKF bundle path.
- Optional approved `RFL-###` references to apply.
- `references/reflect_routing.md`.

## 2. Processes

1. Read the supplied current-session retro. Do not create, revise, or search for a retro.
2. Derive learning items only from supported retro evidence and actions.
3. Assign each learning item a stable `RFL-###` reference.
4. For each item, propose in this order:
   1. A scoped `AGENTS.md` update when it changes short-term agent behavior.
   2. An MKF lookup query when it may be durable reusable knowledge.
   3. An MKF record target when lookup confirms no duplicate or identifies a concept to update.
5. Set each item's promotion status to `not_eligible`, `candidate`, `duplicate`, `promote`, or `defer`.
6. In proposal mode, return proposals only. Do not update files.
7. In explicit apply mode, apply only user-approved `RFL-###` items:
   1. Use `agentsmd` to update the nearest applicable `AGENTS.md`, when proposed.
   2. Use `lookup` before every MKF write.
   3. Use `record` to create or update the selected MKF concept.
   4. Explicitly request index rebuilding through `record`.
8. Report each persisted path, lookup result, record validation result, and index-rebuild result.
9. Preserve each `RFL-###` reference when user feedback changes its target, content, or route.

## 3. Outputs

- Ordered, referenceable `RFL-###` proposals.
- For each proposal: retro evidence, short-term target, lookup query, long-term target, promotion status, and required approval.
- In apply mode: changed paths and validation results.
- Explicit unresolved targets, ambiguous MKF bundles, duplicates, and user decisions needed.

## 4. Next Steps

- `agentsmd` — update an approved short-term directive.
- `lookup` — find related long-term knowledge.
- `record` — persist approved long-term knowledge and rebuild indexes.

## 5. Examples

### Example 1: Propose learning updates

**Prompt:** `/reflect`
**Outcome:** Returns ordered `RFL-###` proposals from the supplied retro without updating files.

### Example 2: Apply approved updates

**Prompt:** `/reflect apply RFL-001 RFL-003`
**Outcome:** Applies only the named proposals in order, using lookup before each MKF record and explicitly rebuilding indexes after every record.

### Example 3: Apply all proposals

**Prompt:** `/reflect apply all`
**Outcome:** Applies every current proposal in displayed order unless an unresolved target, ambiguous MKF bundle, or failed lookup blocks an item.
