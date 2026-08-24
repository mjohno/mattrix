---
type: checklist
title: Critical state consensus checklist
description: Uses distributed consensus safely for critical shared state and coordination.
tags: [engineering, sre, distributed-systems, consensus, critical-state]
sources:
  - resource: https://sre.google/sre-book/managing-critical-state/
---

# Critical state consensus checklist

- [ ] Use consensus only where critical shared state needs coordinated decisions.
- [ ] Select a proven replicated-state, datastore, election, lock, or queue pattern.
- [ ] Prevent split brain and unsafe failover behavior.
- [ ] Use an odd replica count that can maintain the required quorum.
- [ ] Place replicas to tolerate the intended location failures.
- [ ] Plan capacity and load so quorum members remain available.
- [ ] Keep leader behavior stable and batch work when it improves performance.
- [ ] Monitor quorum health, replication, leader changes, latency, and capacity.
