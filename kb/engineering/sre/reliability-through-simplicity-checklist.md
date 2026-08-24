---
type: checklist
title: Reliability through simplicity checklist
description: Reduces accidental complexity to improve service reliability and change safety.
tags:
  - engineering
  - sre
  - reliability
  - simplicity
  - architecture
sources:
  - resource: https://sre.google/sre-book/simplicity/
---

# Reliability through simplicity checklist

Use this checklist to reduce complexity in a production system.

## System design

- [ ] Identify and remove accidental complexity.
- [ ] Keep each component responsible for one clear purpose.
- [ ] Use small APIs with only necessary methods and arguments.
- [ ] Version APIs and data formats when consumers need safe migration.
- [ ] Keep components and configuration loosely coupled where this permits isolated change.

## Code and features

- [ ] Confirm that each feature and code path supports a current business need.
- [ ] Delete dead code, obsolete flags, and unused features.
- [ ] Do not keep commented-out code as a substitute for version control.
- [ ] Detect code and dependency growth that adds cost without value.
- [ ] Push back on additions that create complexity without a clear benefit.

## Change and release

- [ ] Make changes small enough to understand and measure in isolation.
- [ ] Avoid release batches of unrelated changes.
- [ ] Balance delivery speed with service stability.
- [ ] Review whether procedures and tools can be made simpler.
- [ ] Treat simplicity as a reliability requirement, not as reduced engineering effort.
