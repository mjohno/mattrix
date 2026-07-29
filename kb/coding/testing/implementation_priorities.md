---
type: undefined
title: Testing Implementation Priorities
description: Orders testing investment as a system matures.
tags: [testing, implementation, priorities]
---

# Testing Implementation Priorities

Build coverage in this order as the system becomes capable of supporting it:

1. **Type checking and compilation** — establish basic correctness and buildability.
2. **Style and deterministic static analysis** — enforce stable, actionable conventions and code-smell rules.
3. **Local integration tests** — cover core user behavior across local components.
4. **Focused unit tests** — cover uncovered edge cases, invariants, isolated complexity, and critical regressions.
5. **Local-system smoke tests** — verify the deployable system is alive and minimally capable.
6. **System tests against a local deployment** — validate complete full-stack flows repeatably.
7. **System tests against shared development or staging environments** — gain confidence in deployed configuration and infrastructure.
8. **Production smoke checks and carefully scoped production system tests** — verify essential live behavior without destructive effects.

This is an implementation sequence, not the mandatory order in which existing checks execute.

## Related Concepts

- [Testing Boundaries](boundaries.md) defines the test categories used here.
- [Execution Priorities](execution_priorities.md) defines execution order.
