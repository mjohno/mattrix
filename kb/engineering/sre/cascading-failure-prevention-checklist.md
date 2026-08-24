---
type: checklist
title: Cascading failure prevention checklist
description: Prevents and limits failures that spread through dependent services.
tags: [engineering, sre, cascading-failures, resilience]
sources:
  - resource: https://sre.google/sre-book/addressing-cascading-failures/
---

# Cascading failure prevention checklist

- [ ] Identify overload, resource exhaustion, and dependency loss failure paths.
- [ ] Bound queues and shed load before resource exhaustion spreads.
- [ ] Define graceful degradation for noncritical work.
- [ ] Use retries only with limits, backoff, and a clear success condition.
- [ ] Set and propagate realistic deadlines and cancellation.
- [ ] Avoid cold-start and cache behavior that creates synchronized load spikes.
- [ ] Test failure behavior beyond the first point of failure.
- [ ] In an active cascade, reduce traffic, batch work, and bad requests before adding capacity.
