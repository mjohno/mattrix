---
type: checklist
title: Data integrity checklist
description: Preserves recoverable, correct data through layered protection and verified recovery.
tags: [engineering, sre, data-integrity, backups, recovery]
sources:
  - resource: https://sre.google/sre-book/data-integrity/
---

# Data integrity checklist

- [ ] Define data integrity and availability requirements for each data class.
- [ ] Identify deletion, corruption, replication, and recovery failure modes.
- [ ] Use defense in depth: soft deletion, backups, replication, and early detection.
- [ ] Select retention and backup strategy from recovery requirements.
- [ ] Design a recovery system, not only a backup process.
- [ ] Validate data out of band where production reads cannot prove correctness.
- [ ] Test restoration regularly at realistic data scale.
- [ ] Monitor backup completion, replication health, validation results, and recovery readiness.
