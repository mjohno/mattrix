---
type: checklist
title: Distributed periodic scheduling checklist
description: Runs periodic work reliably across distributed systems.
tags: [engineering, sre, scheduling, cron, distributed-systems]
sources:
  - resource: https://sre.google/sre-book/distributed-periodic-scheduling/
---

# Distributed periodic scheduling checklist

- [ ] Define the schedule, deadline, owner, and success condition for each job.
- [ ] Make job execution idempotent or make duplicate work safe.
- [ ] Track job state, attempts, and completion durably.
- [ ] Define behavior for late, missed, partial, and duplicate execution.
- [ ] Use consensus or equivalent coordination where one scheduler decision is required.
- [ ] Separate leader and follower responsibilities and test leader loss.
- [ ] Scale execution without creating synchronized load spikes.
- [ ] Monitor job lateness, failures, retries, and queue growth.
