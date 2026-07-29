---
name: step
description: Provide STEP role packet contracts. Use when an orchestrator needs coordinator, worker, or assessor context.
metadata:
  type: skill
  category: map
---

# step

Goal: Provide reusable role context and YAML packet contracts for one STEP orchestration loop.
Non-Goals: Do not own STEP files, select transitions, render user gates, mutate workflow state, or execute assigned work. `agents/stagger-step` owns those responsibilities.
Use-When: An orchestrator needs coordinator, worker, or assessor instructions and role output contracts for a STEP workflow.

## 0. Prerequisites

- An orchestrator with the goal, approved task, and any role-specific context.
- A role name: `coordinator`, `worker`, or `assessor`.

## 1. Inputs

- Coordinator context: goal, accumulated progress, lessons, assessor actions, and optional user revision.
- Worker context: one approved task, execution context, and workspace paths.
- Assessor context: goal, approved task, and worker evidence.

## 2. Processes

1. Load the role reference and the shared packet contract.
2. Give the role only its declared context; never provide STEP operations or another role's private context.
3. Return the role packet to the orchestrator without STEP state access.
4. The orchestrator normalizes the packet through its owned role-specific boundary and independently validates it against STEP state.

## 3. Outputs

- A coordinator proposal with selected lessons, ranked next-task packets, and recommendation.
- A worker packet with Do and Validate evidence.
- An assessor packet with retro, actions, and optional clarification request.
- No STEP file access or mutation.

## 4. Next Steps

- `agents/stagger-step` — mediate roles, validate state, render gates, and apply approvals.
- `output/check` — evaluate a role packet against additional acceptance criteria.
- `output/review` — inspect role contracts or packet behavior from a selected perspective.

## 5. Examples

### Example 1: Role packets

Each role has its own packet shape. The orchestrator normalizes returned candidate YAML using its owned role-specific boundary before using it.

## Role references

- Coordinator: [`references/coordinator.md`](references/coordinator.md)
- Worker: [`references/worker.md`](references/worker.md)
- Assessor: [`references/assessor.md`](references/assessor.md)
- Shared contract: [`references/packet_contract.md`](references/packet_contract.md)
