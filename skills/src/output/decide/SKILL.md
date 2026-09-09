---
name: decide
description: Use when current context needs one suggested decision, such as a next step or a choice between options.
metadata:
  type: skill
  category: output
---

# decide

Goal: Suggest one best decision from supplied context.
Non-Goals: Do not execute work, approve action, investigate missing facts, or present unsupported certainty.
Use-When: A user asks to decide on a next step, an option, or a course of action.

## 0. Prerequisites

- A decision prompt and relevant current context.

## 1. Inputs

- Decision prompt.
- Available goals, evidence, constraints, risks, and feedback.
- Options and decision criteria, when supplied.
- `references/decision_quality.md`

## 2. Processes

1. Identify the requested decision and relevant supplied context.
2. Identify meaningful options from supplied context. State when options or criteria are missing.
3. Select one suggestion using value, risk, dependency, reversibility, and feasible scope as applicable.
4. State the concise reason, disregarded material options, assumptions, and uncertainties.
5. Do not execute, approve, or imply certainty beyond the evidence.

## 3. Outputs

- One `DEC-###` decision result with a suggestion and concise reason.
- Material disregarded options with reasons.
- Material assumptions and uncertainties.

## 4. Next Steps

- `draft` with `interface/plan` — create a plan for an accepted decision.
- `investigate` — gather missing evidence.
- `grill-me` — challenge assumptions or an uncertain decision.
- `check` — assess the result against `references/decision_quality.md`.

## 5. Examples

### Example 1

**Prompt:** `/skill:decide Decide on the next step for this project.`
**Outcome:** Returns one suggested next step, its reason, disregarded options, and material assumptions or uncertainties.
