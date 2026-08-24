---
type: checklist
title: Automation design checklist
description: Designs safe, observable, and maintainable automation for service operations.
tags:
  - engineering
  - sre
  - automation
  - operations
sources:
  - resource: https://sre.google/sre-book/automation-at-google/
---

# Automation design checklist

Use this checklist to design or review operational automation.

## Need and scope

- [ ] Identify a repeated procedure, common fault, or lifecycle operation.
- [ ] Define the expected result and safe operating boundary.
- [ ] Prefer a system design that needs no external operator action where practical.
- [ ] Use automation for consistency, faster repair, and scalable operation, not only time saving.
- [ ] Avoid automation that hides a necessary long-term system fix.

## Safety and operation

- [ ] Make each change idempotent where practical.
- [ ] Detect inconsistent state before the system serves production traffic.
- [ ] Verify the result of each action.
- [ ] Stop and notify an operator after repeated failure.
- [ ] Apply rate limits and sanity checks to actions with large effects.
- [ ] Provide clear state, logs, and metrics for human diagnosis.

## Ownership and design

- [ ] Keep automation maintained by the team that owns the operated service.
- [ ] Use reviewed APIs with least-privilege access control and audit records.
- [ ] Test infrequent automation and failure paths.
- [ ] Design decoupled subsystems and clear APIs that support autonomous behavior.
- [ ] Review whether the automation still matches the current system.
