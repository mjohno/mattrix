# Spec Contract

A spec is a traceable future-state artifact. It defines what should be true, why it matters, and how it can be judged without becoming an implementation plan.

## Required Shape

```text
# SPEC-<slug>: <Title>

## 1. Purpose
- SPUR-001: <problem, objective, opportunity, or threat>

## 2. Current State Summary
- SCUR-001: <relevant current fact or assumption>

## 3. Future State
- SFUT-001: <desired end condition>

## 4. Scope
### In Scope
- SSIN-001: <included area>
### Out of Scope
- SSOUT-001: <excluded area>

## 5. Requirements
- SREQ-001: <required behavior or property>

## 6. Acceptance
- SACC-001: <observable judgment criterion>

## 7. Quality
### Constraints / Non-Negotiables
- SQCON-001: <hard limit>
### Priorities
- SQPRI-001: <priority>

## 8. Expectations
- SEXP-001: <review, validation, evidence, or handoff expectation>

## 9. Uncertainties
### Risks
- SURISK-001: <risk>
### Questions
- SUQ-001: <question>
### Assumptions
- SUASM-001: <assumption>
### Pre-Work Needed
- SUPRE-001: <investigation, prototype, decision, or validation>

## 10. Decisions
- SDEC-001: <decision, status, and rationale if useful>
```

## Rules

- Define a future state, not an implementation plan.
- Use stable IDs for referenceable claims, not every sentence.
- Keep current facts, future targets, requirements, acceptance, and decisions distinct.
- Make scope boundaries strong enough to reject unrelated work.
- Keep uncertainty visible rather than hiding it in requirements.
- Downstream plans should trace to spec IDs without copying full spec text.

## Minimal Example

```text
# SPEC-login-errors: Login Error Cleanup

## 1. Purpose
- SPUR-001: Users need clear recovery guidance after login failures.

## 3. Future State
- SFUT-001: Each login failure maps to one consistent user-facing message.

## 6. Acceptance
- SACC-001: Review confirms every known login failure has approved copy and recovery guidance.
```
