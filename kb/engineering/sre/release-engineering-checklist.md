---
type: checklist
title: Release engineering checklist
description: Builds reproducible, controlled, and reversible software releases.
tags:
  - engineering
  - sre
  - release-engineering
  - deployment
sources:
  - resource: https://sre.google/sre-book/release-engineering/
---

# Release engineering checklist

Use this checklist to design or review a release process.

## Build and test

- [ ] Make builds reproducible from known source, tools, and dependencies.
- [ ] Record a unique build identifier and source revision for each artifact.
- [ ] Build and test automatically.
- [ ] Run release tests against the exact artifact that will be deployed.
- [ ] Keep a record of changes included in each release.

## Control and delivery

- [ ] Define roles and access controls for source changes, releases, and deployment.
- [ ] Require review for code, build configuration, and service configuration changes.
- [ ] Package and version artifacts so each release is uniquely identifiable.
- [ ] Let service teams run normal releases through a self-service process.
- [ ] Release small, frequent changes when the service risk allows it.

## Deployment and configuration

- [ ] Select rollout speed from the service risk profile and error budget.
- [ ] Use canary deployment before broader rollout where appropriate.
- [ ] Observe the rollout and stop, roll back, or slow it when service indicators degrade.
- [ ] Define a tested rollback method.
- [ ] Version and review configuration; keep its relationship to binaries clear.
- [ ] Include release engineering early in the service lifecycle.
