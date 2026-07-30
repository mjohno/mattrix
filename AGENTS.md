# AGENTS

Mattrix is a single-owner monorepo for reusable skills, MKF knowledge-base implementation, and deterministic agents.

## Domains

- `skills/` owns reusable skill packages and their documentation. Read `skills/AGENTS.md` before modifying this domain.
- `kb/` implements the passive MKF contract owned by `skills/src/interface/knowledge-base/`.
- `agents/` owns agent products.

## Boundaries

- Dependencies flow from `agents` and `kb` to `skills`; no skill or KB component depends on an individual agent.
- `agents/stagger-step` owns STEP state, deterministic transitions, and user gates.
- Pi.dev is a replaceable execution-harness integration behind `agents/stagger-step`; it does not own STEP state.
- Do not add business-data storage or compatibility wrappers for the pre-monorepo layout.
