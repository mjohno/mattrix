---
type: checklist
title: Data processing pipeline checklist
description: Designs reliable distributed pipelines that maintain correctness and predictable load.
tags: [engineering, sre, data-pipelines, workflows]
sources:
  - resource: https://sre.google/sre-book/data-processing-pipelines/
---

# Data processing pipeline checklist

- [ ] Define each stage, its input, output, owner, and correctness condition.
- [ ] Track workflow state and dependencies explicitly.
- [ ] Distribute uneven work without leaving stragglers or hot workers.
- [ ] Avoid periodic schedules that create thundering-herd load.
- [ ] Monitor end-to-end progress, stage delay, failures, and backlog.
- [ ] Make retries and repeated work safe for data correctness.
- [ ] Provide recovery for partial failure and interrupted execution.
- [ ] Test capacity, load patterns, and continuity when a component fails.
