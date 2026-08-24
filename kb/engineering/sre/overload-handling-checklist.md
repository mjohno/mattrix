---
type: checklist
title: Overload handling checklist
description: Protects a service and its users when demand exceeds safe capacity.
tags: [engineering, sre, overload, capacity]
sources:
  - resource: https://sre.google/sre-book/handling-overload/
---

# Overload handling checklist

- [ ] Measure work cost, not only queries per second.
- [ ] Set per-customer limits that prevent one client from harming others.
- [ ] Apply client-side throttling when clients can cooperate.
- [ ] Reserve capacity for critical requests and define their priority.
- [ ] Use direct utilization signals to detect unsafe load.
- [ ] Return explicit overload errors when the service must reject work.
- [ ] Define when clients may retry and prevent retry amplification.
- [ ] Limit connection load as well as request load.
