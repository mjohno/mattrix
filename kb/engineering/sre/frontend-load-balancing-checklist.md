---
type: checklist
title: Frontend load balancing checklist
description: Routes client traffic to healthy frontend capacity with resilient global behavior.
tags: [engineering, sre, load-balancing, frontend]
sources:
  - resource: https://sre.google/sre-book/load-balancing-frontend/
---

# Frontend load balancing checklist

- [ ] Define the client traffic entry points and routing objectives.
- [ ] Use DNS and virtual-IP routing according to their failure and control limits.
- [ ] Direct traffic only to healthy, available serving locations.
- [ ] Plan for failures of routes, sites, and load-balancing components.
- [ ] Preserve capacity for traffic shifts during a location failure.
- [ ] Measure routing success, latency, and load distribution from the client view.
- [ ] Test traffic changes and failover paths before an emergency.
