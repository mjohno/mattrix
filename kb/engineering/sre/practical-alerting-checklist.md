---
type: checklist
title: Practical alerting checklist
description: Designs reliable time-series alerting and its supporting monitoring configuration.
tags: [engineering, sre, monitoring, alerting]
sources:
  - resource: https://sre.google/sre-book/practical-alerting/
---

# Practical alerting checklist

- [ ] Export service metrics with stable names, labels, and units.
- [ ] Collect and retain time-series data at useful resolution.
- [ ] Define rules that turn measurements into actionable conditions.
- [ ] Send alerts to an owned, maintained notification path.
- [ ] Use black-box probes for important user journeys.
- [ ] Shard monitoring components before their load affects collection or alerting.
- [ ] Keep monitoring configuration in reviewable source control.
- [ ] Test alert delivery and rule changes.
