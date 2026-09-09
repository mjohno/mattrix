---
name: navigate
description: Use when current context needs one referenceable next-best task and execution recommendation.
metadata:
  type: skill
  category: output
---

# navigate

Goal: Turn current context into one next-best task and recommended execution route.
Non-Goals: Do not execute work, launch sub-agents, create worker profiles, or split work into an action chain.
Use-When: A user invokes `/skill:navigate` with optional guidance to determine the next best course of action.

## 0. Prerequisites

- Current context, results, feedback, constraints, or `RFL-###` items.
- The `task` skill.
- Available named worker profiles, a `default-worker` profile, or the current session.

## 1. Inputs

- Current goals, evidence, feedback, risks, and unresolved items.
- Optional user guidance supplied with `/skill:navigate`.
- Available worker-profile names, roles, tools, models, and boundaries.
- `references/navigate_routing.md`

## 2. Processes

1. Treat optional user guidance as contextual input for the assessment.
2. Analyze the current context as a system. Generate a small set of meaningful outcome candidates, not a sequence of small actions.
3. Select the best outcome by value, leverage, risk reduction, dependency removal, reversibility, confidence, and feasible scope. State material uncertainty and rejected alternatives.
4. Use `task` to create one bounded INVEST task statement with observable completion evidence.
5. Select the best execution route and create a stable `NAV-###` packet with the task, supporting context, and concise reasoning.

## 3. Outputs

- One referenceable `NAV-###` recommendation.
- One task-skill statement.
- One selected execution route: matching worker profile, `default-worker`, or current session.
- Relevant paths, source references, feedback, constraints, and material uncertainty needed for execution.

## 4. Next Steps

- `execute NAV-###` — perform approved work in the current thread.
- `delegate NAV-### [guidance]` — launch the selected worker with the task packet.
- `outline` — propose structure, paths, or a missing worker profile.
- `draft` — create approved new content.
- `modify` — apply approved focused changes.
- `fix` — apply approved corrections, when available.

## 5. Examples

### Example 1

**Prompt:** `/skill:navigate Reduce repeated retro work.`
**Outcome:** Returns one `NAV-001` task statement, selected worker route, rationale, relevant context, and uncertainty without executing work.
