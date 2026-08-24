---
type: checklist
title: Reliable product launch checklist
description: Coordinates product launches so architecture, capacity, failure handling, and rollout risk are ready.
tags: [engineering, sre, product-launch, release, reliability]
sources:
  - resource: https://sre.google/sre-book/reliable-product-launches/
---

# Reliable product launch checklist

- [ ] Assign a launch coordinator and owners for open risks.
- [ ] Document architecture, dependencies, and integration points.
- [ ] Verify capacity plans against expected and abusive client behavior.
- [ ] Identify failure modes and define safe degraded behavior.
- [ ] Confirm client retry, caching, and error behavior under failure.
- [ ] Review operational processes, automation, monitoring, and on-call readiness.
- [ ] Confirm the development and change-control process supports launch risk.
- [ ] Assess external dependency limits and failure behavior.
- [ ] Use staged rollout, feature controls, load tests, and explicit rollback conditions.
