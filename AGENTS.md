# AGENTS

Mattrix is a single-owner monorepo for reusable skills, MKF knowledge-base implementation, and deterministic agents.

## Domains

- `skills/` owns reusable skill packages and their documentation.
- `kb/` implements the passive MKF contract owned by `skills/src/interface/knowledge-base/`.
- `agents/` owns agent products.

## Projects

- `agents/stagger-step/README.md`: A deterministic loop which launches a single agent at a time to complete the next best task.

# Instructions

## Rules

- Read `skills/AGENTS.md` before modifying `skills/`.
- Maintain dependency flow from `agents` and `kb` to `skills`; do not let a skill or KB component depend on an individual agent.

## Constraints

- Do not add business-data storage or compatibility wrappers for the pre-monorepo layout.
