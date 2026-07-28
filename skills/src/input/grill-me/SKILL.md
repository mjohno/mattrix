---
name: grill-me
description: Filters assumptions and risks through adversarial questioning — interviewing the user to stress-test plans and designs.
metadata:
  category: input
  capabilities:
    - adversarial_validation
    - stress_test_interview
---

# grill-me

Goal: Interview the user relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.
Non-Goals: Do not create implementation plans, execute tasks, or make decisions on behalf of the user.
Use-When: You need to stress-test a plan or design by exploring all decision branches.

## 0. Prerequisites
- A plan, design, or proposal to interrogate

## 1. Inputs
- Plan, design, or proposal content from prompt
- User context and constraints (optional)

## 2. Processes
1. Parse the plan/design to identify all decision points and assumptions
2. For each decision branch, ask one question at a time
3. Provide a recommended answer with reasoning for each question
4. Explore dependencies between decisions and resolve them
5. Flag unresolved assumptions or hidden risks
6. Stop when all decision branches are resolved or the user indicates stopping

## 3. Outputs
- Structured output in the prompt with resolved decisions, remaining questions, and flagged risks
- If user specifies an output file, write to that path instead

## 4. Next Steps
- `modify` with `interface/plan` — if the plan needs restructuring based on findings
- `output/review` — if findings need structured critique against specs or personas
- `output/check` — if decisions, claims, or assumptions need validation against criteria or evidence

## 5. Examples

### Example 1: Plan stress test

**Prompt:** Grill me on the zero-trust migration plan.

**Outcome:** Sequential questioning that reveals 3 unresolved assumptions, 2 hidden risks, and 5 decisions that need user input before proceeding.

### Example 2: Design critique

**Prompt:** Grill me on the microservices architecture design.

**Outcome:** Questions that expose tight coupling between services, missing error handling assumptions, and unclear ownership boundaries.
