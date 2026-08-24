---
type: checklist
title: Toil reduction checklist
description: Identifies and reduces recurring operational work without lasting value.
tags:
  - engineering
  - sre
  - operations
  - toil
sources:
  - resource: https://sre.google/sre-book/eliminating-toil/
---

# Toil reduction checklist

Use this checklist to manage recurring operational work.

## Identify toil

- [ ] List work required to run the production service.
- [ ] Mark work that is manual, repetitive, automatable, tactical, or without lasting value.
- [ ] Identify work that grows linearly with service size.
- [ ] Separate toil from necessary overhead and from engineering work.
- [ ] Measure toil by person and team over a useful period.

## Reduce toil

- [ ] Keep operational toil below half of engineering time over the long term.
- [ ] Share on-call and interrupt work fairly across the team.
- [ ] Prioritize engineering projects that remove the largest recurring toil.
- [ ] Replace repeated human response with automation or better system design.
- [ ] Treat frequent, complex human responses as a design problem to remove.

## Sustain improvement

- [ ] Review toil trends at regular intervals.
- [ ] Investigate teams or people with sustained excessive toil.
- [ ] Reserve time for work that improves reliability, performance, utilization, or scale.
- [ ] Verify that each improvement reduces future operational effort.
