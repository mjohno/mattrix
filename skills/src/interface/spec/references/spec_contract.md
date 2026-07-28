# Spec Contract

A spec is a traceable future-state artifact. It defines what should be true, why it matters, and how it can be judged without becoming an implementation plan.

## Required Shape

```text
# SPEC-<slug>: <Title>

## 1. Purpose
- PUR-001: <problem, objective, opportunity, or threat>

## 2. Current State Summary
- CUR-001: <relevant current fact or assumption>

## 3. Future State
- FUT-001: <desired end condition>

## 4. Scope
### In Scope
- SCP-IN-001: <included area>
### Out of Scope
- SCP-OUT-001: <excluded area>

## 5. Requirements
- REQ-001: <required behavior or property>

## 6. Acceptance
- ACC-001: <observable judgment criterion>

## 7. Quality
### Constraints / Non-Negotiables
- QUA-CON-001: <hard limit>
### Priorities
- QUA-PRI-001: <priority>

## 8. Expectations
- EXP-001: <review, validation, evidence, or handoff expectation>

## 9. Uncertainties
### Risks
- UNC-RISK-001: <risk>
### Questions
- UNC-Q-001: <question>
### Assumptions
- UNC-ASM-001: <assumption>
### Pre-Work Needed
- UNC-PRE-001: <investigation, prototype, decision, or validation>

## 10. Decisions
- DEC-001: <decision, status, and rationale if useful>
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
- PUR-001: Users need clear recovery guidance after login failures.

## 3. Future State
- FUT-001: Each login failure maps to one consistent user-facing message.

## 6. Acceptance
- ACC-001: Review confirms every known login failure has approved copy and recovery guidance.
```
