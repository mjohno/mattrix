---
type: checklist
title: Kubernetes autoscaling checklist
description: Checks for safe, measurable, and reliable Kubernetes workload autoscaling.
tags:
  - devops
  - kubernetes
  - autoscaling
  - capacity
---

# Kubernetes autoscaling checklist

Use this checklist when you configure or review Kubernetes workload autoscaling.

## Scaling decision

- [ ] Confirm that autoscaling is required for the workload's traffic pattern and availability target.
- [ ] Select horizontal, vertical, event-driven, scheduled, or cluster autoscaling for a documented reason.
- [ ] Do not use autoscaling to hide an application performance, memory, or dependency failure.
- [ ] Define the workload owner, scaling objective, and acceptable response time.

## Metrics and resource requests

- [ ] Set CPU and memory requests for every container before using resource-based HorizontalPodAutoscaling.
- [ ] Use a metric that represents the workload constraint, such as CPU, memory, queue depth, request rate, or latency.
- [ ] Confirm that the metrics API provides complete, current metrics for the target workload.
- [ ] Define a target metric value from measured workload behavior.
- [ ] Test metric behavior when Pods are starting, unready, missing, or terminating.
- [ ] Alert when scaling metrics are unavailable, stale, or outside their expected range.

## Horizontal Pod Autoscaler

- [ ] Set explicit minimum and maximum replica counts.
- [ ] Set a maximum replica count that the cluster and backing services can support.
- [ ] Configure scale-up policies that meet the required response time without overloading dependencies.
- [ ] Configure scale-down policies and a stabilization window to prevent flapping.
- [ ] Test the HorizontalPodAutoscaler under normal load, burst load, and reduced load.
- [ ] Confirm that readiness probes prevent unready Pods from receiving traffic during scale-out.
- [ ] Confirm that the application can safely run at every replica count between the minimum and maximum.

## Vertical and event-driven scaling

- [ ] Use Vertical Pod Autoscaler only when its update behavior is compatible with workload disruption requirements.
- [ ] Review Vertical Pod Autoscaler recommendations before automatic application.
- [ ] Do not let Vertical Pod Autoscaler and HorizontalPodAutoscaler control the same CPU or memory target without an approved design.
- [ ] Define event-source credentials, lag limits, and failure behavior for event-driven scaling.
- [ ] Test event-driven scale-to-zero, scale-from-zero, and event-source outage behavior when they are enabled.

## Capacity and availability

- [ ] Confirm that cluster capacity can schedule the maximum replica count.
- [ ] Configure cluster autoscaling when workload autoscaling can exceed available cluster capacity.
- [ ] Confirm that node, IP-address, storage, quota, and external-service limits support the maximum scale.
- [ ] Set a PodDisruptionBudget when voluntary disruptions could reduce required availability.
- [ ] Load-test the application and backing services at the expected maximum scale.

## Operations

- [ ] Monitor desired replicas, current replicas, scaling events, pending Pods, and scaling latency.
- [ ] Alert when the workload reaches its maximum replica count or cannot schedule new Pods.
- [ ] Record manual scaling overrides and return the workload to its declared scaling configuration.
- [ ] Review autoscaling configuration after major traffic, application, metric, or dependency changes.

## Reference

- [Kubernetes Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Kubernetes autoscaling workloads](https://kubernetes.io/docs/concepts/workloads/autoscaling/)
- [Kubernetes resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
