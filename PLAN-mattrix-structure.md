# Plan: Mattrix Skills and KB Structural Refactor

PLAN_ID: PLAN-mattrix-structure
Source: SPEC-mattrix.md
Purpose: Transform the current skills repository into the bounded Mattrix monorepo structure, with the MKF contract in skills and its implementation in KB.

## Source Summary

- FUT-001 through FUT-004: Mattrix is a monorepo with `skills`, `kb`, and `agents` domains; only `stagger-step` is initially implemented.
- REQ-001 and REQ-002: Domains own their local source/docs roots; `skills/src/interface/knowledge-base` owns MKF and `kb/src` implements it.
- QUA-CON-004 and EXP-002: Skill paths are relative to `SKILL.md`, documentation paths are relative to their docs root, and relocation is a clean break.

## Gap Map

| Gap ID | Source Summary | Current Problem | Target State |
| --- | --- | --- | --- |
| GAP-1 | FUT-001, FUT-002, REQ-001 | The repository root is the skills domain, with `src/` and `docs/` at root. | Mattrix has bounded top-level `skills/`, `kb/`, and `agents/` domains; skills reside at `skills/src/` and `skills/docs/`. |
| GAP-2 | FUT-003, REQ-002 | No first-class KB domain or local MKF implementation exists. | `skills/src/interface/knowledge-base/` defines MKF and `kb/src/` implements it, with KB documentation under `kb/docs/`. |
| GAP-3 | FUT-004, SCP-OUT-004 | The target agent domain is not structurally defined; `rfc` has no concrete responsibility. | The structure supports agent products while only the concrete `stagger-step` product is introduced; `agents/rfc/` remains absent. |
| GAP-4 | QUA-CON-004, EXP-002 | Existing contents must move without compatibility scaffolding or incorrect root-relative references. | Moved skills and documentation retain correct local-relative references, and observed violations are repaired. |

## Work Plan

### PLAN-mattrix-structure-1 — Establish bounded monorepo roots
Closes: GAP-1, GAP-3
Source refs: FUT-001, FUT-002, FUT-004, REQ-001
Status: done
Depends on: none
Outcome: Mattrix has explicit domain roots and only the intended initial agent-product scaffold.

Deliverables:
- Root `skills/`, `kb/`, and `agents/` directories.
- `agents/stagger-step/` product roots for `src/`, `docs/`, and `tests/`.
- Root-level documentation describing domain ownership, the Pi.dev harness-adapter boundary for `stagger-step`, and deferred `agents/rfc/` status.

Done when:
- Repository inspection shows the required domain roots and `agents/stagger-step/{src,docs,tests}`.
- `agents/rfc/` is absent.
- Domain ownership, dependency direction, and the replaceable Pi.dev harness boundary are documented.

### PLAN-mattrix-structure-2 — Relocate the skills domain
Closes: GAP-1, GAP-4
Source refs: FUT-002, SCP-IN-003, QUA-CON-004, EXP-002
Status: done
Depends on: PLAN-mattrix-structure-1
Outcome: The existing skill source and documentation operate from `skills/src/` and `skills/docs/`.

Deliverables:
- Relocated skill packages under `skills/src/`.
- Relocated supporting documentation under `skills/docs/`.
- Updated local references for any observed relocation failure.

Done when:
- The prior root `src/` and `docs/` contents are available only through the `skills/` domain.
- Skill package references resolve relative to their `SKILL.md` files.
- Documentation references resolve relative to their documentation root.

### PLAN-mattrix-structure-3 — Establish the MKF contract and KB implementation boundary
Closes: GAP-2
Source refs: FUT-003, REQ-002, DEC-009
Status: done
Depends on: PLAN-mattrix-structure-2
Outcome: MKF contract ownership and KB implementation ownership are separate and explicit.

Deliverables:
- `skills/src/interface/knowledge-base/` package defining the MKF contract.
- `kb/src/` implementation root consuming that contract.
- `kb/docs/` documentation describing the implementation boundary.

Done when:
- The KB contract is located in the skills interface domain.
- KB source and documentation roots exist and identify MKF as their governing contract.
- No dependency from the MKF contract back to an individual agent product is introduced.

### PLAN-mattrix-structure-4 — Verify structural boundaries
Closes: GAP-1, GAP-2, GAP-3, GAP-4
Source refs: ACC-001, ACC-007, QUA-CON-003
Status: done
Depends on: PLAN-mattrix-structure-3
Outcome: The monorepo layout and ownership boundaries are demonstrably correct.

Deliverables:
- Structural verification evidence.
- Recorded observed-and-repaired relocation issues, if any.

Done when:
- The target layout satisfies ACC-001.
- Mattrix does not present business-data storage as a responsibility.
- The domains can be extracted later without reversing their dependency direction.
