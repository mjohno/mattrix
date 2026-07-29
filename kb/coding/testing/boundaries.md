---
type: undefined
title: Testing Boundaries
description: Defines testing categories by observability and system boundary.
tags: [testing, boundaries, white-box, black-box]
---

# Testing Boundaries

Testing boundaries describe what a test can observe and control, not where it runs.

## Local / White-Box

Local tests run against code and dependencies controlled within the development workspace. They may inspect implementation details and directly control collaborators.

### Integration Tests

Integration tests exercise the interactions among local components to cover the bulk of functional user behavior. They are the primary local behavior tests.

### Unit Tests

Unit tests cover meaningful risks not adequately covered by integration tests: edge cases, invariants, complex isolated logic, and critical regressions. Avoid high-churn tests coupled to implementation details. Do not add unit tests when linting or integration tests already provide sufficient coverage.

## Non-Local / Black-Box

Black-box tests use only externally observable interfaces. They do not depend on implementation details, but may run against a local deployment, a shared development environment, or production.

### Smoke Tests

Smoke tests quickly verify that critical components are available and that the system provides its minimum essential capability.

### System Tests

System tests validate complete cross-component user flows through deployed interfaces. They may target a locally deployed system for repeatable full-stack validation, a shared development or staging environment for configuration and infrastructure confidence, or production when the checks are safe and non-destructive.

## Related Concepts

- [Implementation Priorities](implementation_priorities.md) defines when to build each kind of coverage.
- [Execution Priorities](execution_priorities.md) defines the order to run checks.
