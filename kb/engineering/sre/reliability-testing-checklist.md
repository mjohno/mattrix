---
type: checklist
title: Reliability testing checklist
description: Tests service reliability from unit behavior through production operation.
tags: [engineering, sre, testing, reliability]
sources:
  - resource: https://sre.google/sre-book/testing-reliability/
---

# Reliability testing checklist

- [ ] Run unit, integration, and system tests for expected behavior.
- [ ] Test production configuration before and during deployment.
- [ ] Use stress, canary, and production probe tests where appropriate.
- [ ] Keep the test and build environment reproducible.
- [ ] Test the tools and infrastructure that run tests at scale.
- [ ] Exercise disaster and recovery scenarios.
- [ ] Make tests fast enough to guide normal development and release work.
- [ ] Treat failed tests as evidence to investigate, not noise to bypass.
