---
type: checklist
title: Service level objectives checklist
description: Defines measurable service indicators and objectives that reflect user needs.
tags:
  - engineering
  - sre
  - reliability
  - slo
  - sli
sources:
  - resource: https://sre.google/sre-book/service-level-objectives/
---

# Service level objectives checklist

Use this checklist to define or review service level objectives.

## Indicators

- [ ] Identify the service behavior that users value.
- [ ] Select only the few indicators that represent that behavior.
- [ ] Define the success, latency, throughput, availability, durability, or correctness measure as needed.
- [ ] Use client-side measurement when it better represents the user experience.
- [ ] Define the requests, units of work, scope, and measurement source.
- [ ] Use percentiles or distributions when averages hide important tail behavior.

## Objectives

- [ ] State each objective as a measurable target or range.
- [ ] Define the aggregation method and measurement window.
- [ ] Set targets with product, business, and reliability stakeholders.
- [ ] Allow a realistic failure rate instead of requiring perfect performance.
- [ ] Define separate objectives for workloads with different needs.
- [ ] Standardize common indicator definitions and defaults.

## Operation

- [ ] Compare current indicator values with each objective.
- [ ] Define the action to take when an objective is at risk or missed.
- [ ] Use the error budget to guide release and reliability decisions.
- [ ] Publish service expectations for its users.
- [ ] State any separate service-level agreement and its consequences.
