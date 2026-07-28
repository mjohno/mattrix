---
name: walkthrough
description: Guide a user through a required, mutable scope to build understanding through adaptive discussion, evidence, and user-directed creation. Use when the user asks to be brought up to speed, requests a crash course, or wants to walk through a code change, topic, or concept.
metadata:
  type: skill
  category: map
---

# walkthrough

Goal: Progressively explore a required, user-defined scope until the user asks to stop, building understanding through discussion, evidence, and user-directed creation.
Non-Goals: Do not coordinate delivery work, impose a fixed curriculum, assess mastery, maintain persistent state, independently implement changes, or end because the agent considers exploration complete.
Use-When: A user asks to be brought up to speed, requests a crash course, wants to walk through a large review or change, or wants to learn a topic in relation to current content.

## 0. Prerequisites

- A scope covering a code area, change, topic, concept, current content, or combination.
- If the scope is absent or too vague to orient, ask the user to provide or refine it before proceeding.

## 1. Inputs

- Required current scope and available context, such as files, diffs, content, links, or a concept to learn.
- Optional starting question, desired depth, prior knowledge, or preferred order.
- User questions, deferrals, returns to skipped material, and scope changes throughout the walkthrough.

## 2. Processes

1. **Orient**: Read relevant context and establish a short mental model of the current scope. Git comparisons are optional evidence, not a required starting point.
2. **Map coverage**: Keep a lightweight prompt-only view of explored, active, deferred or skipped, and newly added areas. Do not create persistent state unless the user asks.
3. **Guide**: Explain one connected area at a time using evidence, examples, and its relationship to the broader scope. Suggest a useful next area without imposing an order.
4. **Adapt**: Answer clarifying questions; revisit foundations, follow a relevant tangent, or resume a deferred area as the user directs.
5. **Update scope**: When the user expands, narrows, replaces, or redirects the scope, explicitly notify the user of the change and update the prompt-only coverage view.
6. **Create on direction**: Create, modify, or annotate only when the user explicitly requests it in service of understanding. Use focused downstream skills when applicable.
7. **Continue**: Keep exploring the current scope, including deferred areas when the user returns to them. Do not autonomously declare it exhausted or complete; stop only when the user asks to stop or is satisfied.

## 3. Outputs

- User-paced explanations, examples, and evidence grounded in the current scope.
- Explicit scope-change notices, for example: `Scope update: adding error propagation; deferring test coverage.`
- Prompt-only coverage context and only those files or artifacts the user explicitly requests.

## 4. Next Steps

- `annotate` — add or update learning-oriented inline annotations.
- `investigate` — gather exhaustive evidence for a bounded unanswered question.
- `check` — validate an outcome against explicit criteria.
- `review` — evaluate an artifact or change through supplied criteria or a persona lens.

## 5. Examples

### Example 1: Large change walkthrough

**Prompt:** "Walk me through the authentication changes between `main` and this branch. Start with the request flow."
**Outcome:** Orients from the relevant diff and code, explains the request flow in connected steps, tracks deferred areas in chat, and continues until the user stops.

### Example 2: Learning with a scope change

**Prompt:** "Give me a crash course on caching in this service."
**Outcome:** Explains the local caching model. If the user asks to also cover invalidation, reports `Scope update: adding cache invalidation`, then continues through that area; an explicitly requested annotation or tweak is made without turning the walkthrough into autonomous implementation.
