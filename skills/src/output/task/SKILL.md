---
name: task
description: Use when supplied context needs a concise, well-written INVEST task statement.
metadata:
  type: skill
  category: output
---

# task

Goal: Turn supplied context into one concise, actionable INVEST task statement.
Non-Goals: Do not implement work, manage plans, assign IDs or status, extract structured task artifacts, or claim verification that has not occurred.
Use-When: Context such as a request, plan item, finding, or specification needs a bounded task a person can understand and complete.

## 0. Prerequisites

- Enough context to identify the intended outcome; retain missing material as an explicit uncertainty.

## 1. Inputs

- Supplied request, source artifact, finding, or implementation context.
- Known target, constraints, dependencies, and completion evidence, when available.

## 2. Processes

1. Identify one smallest useful outcome and its value.
2. Bound the work to one coherent change without prescribing an unneeded solution.
3. Write one prose paragraph of a few sentences that names the change, scope or target, relevant constraint, and observable completion evidence.
4. Mark material unknowns as assumptions or unknowns rather than inventing them.
5. Check the statement against the quality checklist before returning it.

### Quality Checklist

- [ ] It is one paragraph of a few sentences about one bounded change.
- [ ] It states value, scope or target, a relevant constraint, and observable completion evidence.
- [ ] **Independent:** It can proceed without another task, or names a material dependency.
- [ ] **Negotiable:** It specifies the outcome without prematurely fixing the implementation.
- [ ] **Valuable:** It states a user, stakeholder, or objective benefit.
- [ ] **Estimable:** Its bounded scope supplies enough context to estimate effort.
- [ ] **Small:** It describes one coherent change suitable for one unit of work.
- [ ] **Testable:** It gives observable completion evidence.
- [ ] It labels material uncertainty rather than presenting it as fact.

## 3. Outputs

- One reviewable task statement, prose only, limited to one paragraph.

## 4. Next Steps

- `check` — validate the statement against its intended context or acceptance criteria.
- `step` — execute an approved task statement.
- `plan` — sequence multiple task statements when one task is insufficient.

## 5. Examples

### Example 1

**Prompt:** Draft a task from the finding that login errors reveal whether an account exists.
**Outcome:** Return one bounded paragraph describing normalized login failures, the affected login path, the need to preserve error-code behavior, and test evidence that both unknown-account and wrong-password responses are indistinguishable.
