---
name: goal
description: Use when supplied context needs a concise, well-written SMART goal statement.
metadata:
  type: skill
  category: output
---

# goal

Goal: Turn supplied context into one clear, assessable SMART goal statement.
Non-Goals: Do not elicit priorities, choose work, execute work, or claim that a goal has been achieved.
Use-When: A request, objective, or initiative needs a measurable intended outcome with bounded scope and timing.

## 0. Prerequisites

- Enough context to identify an intended outcome; retain missing facts as explicit assumptions.

## 1. Inputs

- Supplied objective, stakeholder need, scope, baseline, target, deadline, and available evidence source, when known.

## 2. Processes

1. Identify one outcome, its bounded scope, and why it matters.
2. State a measurable target, baseline, and evidence source when available.
3. State the capability, resources, or assumptions that make the outcome plausible.
4. State a deadline or review date.
5. Check the statement against the quality checklist before returning it.

### Quality Checklist

- [ ] **Specific:** It states one outcome and bounded scope.
- [ ] **Measurable:** It names a metric, baseline or baseline assumption, target, and evidence source.
- [ ] **Achievable:** It states capability, resources, or assumptions supporting achievability.
- [ ] **Relevant:** It names a relevant objective or stakeholder value.
- [ ] **Time-bound:** It states a deadline or review date.
- [ ] It labels material unknowns as assumptions.

## 3. Outputs

- One reviewable SMART goal statement in concise prose.

## 4. Next Steps

- `check` — validate the goal against stakeholder needs or acceptance criteria.
- `task` — derive one bounded next unit of work from an approved goal.
- `plan` — sequence the work required to reach an approved goal.

## 5. Examples

### Example 1

**Prompt:** Draft a goal for reducing response times for the search API.
**Outcome:** Return one concise statement that names the search API scope, response-time metric, baseline or assumption, target, evidence source, relevant customer impact, feasibility assumption, and deadline.
