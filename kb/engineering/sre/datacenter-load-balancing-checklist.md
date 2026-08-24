---
type: checklist
title: Datacenter load balancing checklist
description: Distributes requests across healthy service tasks inside a datacenter.
tags: [engineering, sre, load-balancing, datacenter]
sources:
  - resource: https://sre.google/sre-book/load-balancing-datacenter/
---

# Datacenter load balancing checklist

- [ ] Identify unhealthy tasks before they degrade the service.
- [ ] Remove or drain unhealthy tasks with flow control or lame-duck state.
- [ ] Limit each client connection pool with suitable subsetting.
- [ ] Choose a subset method that balances stability and distribution.
- [ ] Use a policy that fits equal or varying request cost.
- [ ] Account for machine diversity and unpredictable performance.
- [ ] Measure task load and use least-loaded or weighted selection where needed.
- [ ] Test task loss, connection churn, and uneven load behavior.
