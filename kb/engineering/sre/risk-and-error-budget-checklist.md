---
type: checklist
title: Risk and error-budget checklist
description: Sets a service reliability target and uses its error budget to control change risk.
tags:
  - engineering
  - sre
  - reliability
  - risk
  - error-budget
sources:
  - resource: https://sre.google/sre-book/embracing-risk/
---

# Risk and error-budget checklist

Use this checklist to set and operate a service error budget.

## Risk target

- [ ] Identify the users, business owner, and reliability owner.
- [ ] Define the user effect of an unplanned failure.
- [ ] Select a reliability target that matches user need and business risk.
- [ ] Consider the cost and value of a higher reliability target.
- [ ] Define separate service classes when clients need different reliability, latency, or throughput.

## Error budget

- [ ] Define a measurement window for the target.
- [ ] Define successful and unsuccessful requests or units of work.
- [ ] Calculate the permitted failure rate from the target.
- [ ] Measure actual performance with a neutral monitoring system.
- [ ] Make the remaining error budget visible to product and reliability teams.

## Change control

- [ ] Allow normal releases while the error budget remains healthy.
- [ ] Define actions as the budget becomes low, such as slower rollout or rollback.
- [ ] Stop or limit releases when the budget is exhausted.
- [ ] Prioritize reliability work before normal release speed resumes.
- [ ] Review whether the target still matches user and business needs.
