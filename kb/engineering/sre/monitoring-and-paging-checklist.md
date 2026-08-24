---
type: checklist
title: Monitoring and paging checklist
description: Builds simple monitoring and paging that detects urgent user-visible problems.
tags:
  - engineering
  - sre
  - monitoring
  - alerting
  - paging
sources:
  - resource: https://sre.google/sre-book/monitoring-distributed-systems/
---

# Monitoring and paging checklist

Use this checklist to create or review monitoring and paging rules.

## Coverage

- [ ] Monitor latency, traffic, errors, and saturation.
- [ ] Measure tail latency where it affects user experience.
- [ ] Use measurement resolution that can reveal meaningful changes.
- [ ] Use black-box checks for current user-visible symptoms.
- [ ] Use white-box data to detect imminent faults and help diagnosis.

## Paging

- [ ] Page only for an urgent, actionable, user-visible or imminent problem.
- [ ] Confirm that the page has a useful human response.
- [ ] Prefer symptom-based pages over pages for every possible cause.
- [ ] Filter known benign states, such as drained traffic or test deployments.
- [ ] Remove duplicate pages that notify multiple people about one problem.
- [ ] Automate a safe, repeated, algorithmic response instead of paging for it.

## Maintainability

- [ ] Keep collection, aggregation, dashboards, and paging rules simple.
- [ ] Provide diagnosis data without making paging depend on complex causality rules.
- [ ] Remove unused signals and rules that do not support a dashboard or alert.
- [ ] Review page frequency, noise, and response quality regularly.
- [ ] Prioritize root-cause removal when a page becomes frequent.
