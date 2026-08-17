---
type: undefined
title: Testing Execution Priorities
description: Orders checks for efficient feedback and delivery confidence.
tags: [testing, execution, priorities, ci]
---

# Testing Execution Priorities

Run checks from the fastest deterministic feedback to broader deployed-system confidence:

1. **Type checking and compilation**
2. **Style and deterministic static analysis**
3. **Local integration tests**
4. **Focused unit tests for uncovered risk**
5. **Black-box smoke tests**
6. **Black-box system tests**

Smoke tests precede system tests because they provide fast confirmation that critical components and minimum capability are available. System tests then validate complete cross-component user flows.

The black-box target is selected for the required confidence: local deployment for repeatability, shared development or staging for deployed-environment confidence, and production only for safe, non-destructive checks.

## Related Concepts

- [Testing Boundaries](boundaries.md) defines the categories and environments.
- [Implementation Priorities](implementation_priorities.md) defines when to build coverage.
