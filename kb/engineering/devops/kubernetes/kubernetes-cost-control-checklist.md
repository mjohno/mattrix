---
type: checklist
title: Kubernetes cost-control checklist
description: Checks for accountable, efficient, and safe Kubernetes cost control.
tags:
  - devops
  - kubernetes
  - cost
  - finops
---

# Kubernetes cost-control checklist

Use this checklist when you review Kubernetes cost, capacity, and resource use.

For workload resource definitions, use the [Kubernetes workload quality checklist](kubernetes-workload-quality-checklist.md).

## Resource right-sizing

- [ ] Review CPU, memory, and ephemeral-storage requests against observed use at a defined interval.
- [ ] Reduce sustained unused requests. Investigate sustained use near a request or limit.
- [ ] Review resources for every container, including sidecars.
- [ ] Do not set CPU limits unless their throttling effect is understood and accepted.
- [ ] Use namespace `LimitRange` defaults where teams do not set valid resources.

## Autoscaling

- [ ] Use HorizontalPodAutoscaler only with suitable utilization or application metrics and defined minimum and maximum replicas.
- [ ] Set HorizontalPodAutoscaler scale-up and scale-down behavior to prevent replica flapping.
- [ ] Do not combine HorizontalPodAutoscaler with VerticalPodAutoscaler on the same CPU or memory target unless the configuration supports that combination.
- [ ] Set VerticalPodAutoscaler to recommendation-only before automatic updates where availability risk is unknown.
- [ ] Configure node autoscaling to remove underused nodes and retain capacity required for workload scheduling.
- [ ] Do not scale a workload to zero when its latency, warm-up, or availability requirements prevent it.

## Tenant controls and ownership

- [ ] Apply `ResourceQuota` for CPU, memory, storage, object count, and workload count per namespace.
- [ ] Label workloads, namespaces, and persistent volumes with owner, application, environment, and cost-allocation fields.
- [ ] Enforce required cost-allocation labels through admission policy or GitOps validation.
- [ ] Assign an accountable owner for each namespace and review unowned resources.
- [ ] Detect and remove orphaned workloads, completed Jobs, unused Services, and unused load balancers.

## Storage and network cost

- [ ] Set storage requests through PersistentVolumeClaim definitions.
- [ ] Review unattached volumes, retained persistent volumes, snapshots, and excessive storage classes.
- [ ] Select storage classes by required availability and performance, not by the highest default tier.
- [ ] Monitor cross-zone, cross-region, and external network-transfer costs.
- [ ] Keep communicating components close when practical.

## Observability and governance

- [ ] Collect requested, allocatable, and actual CPU, memory, storage, and replica metrics.
- [ ] Report cost and utilization by owner, namespace, application, environment, and cluster.
- [ ] Alert on quota pressure, idle capacity, unschedulable Pods, and unexpected cost changes.
- [ ] Review savings actions and their availability impact before applying them.
- [ ] Test that cost-reduction automation cannot evict protected or critical workloads.

## Reference

- [Resource management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Resource quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
- [Limit ranges](https://kubernetes.io/docs/concepts/policy/limit-range/)
- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Kubernetes labels and selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)
- [FinOps Foundation: Kubernetes](https://www.finops.org/framework/technical-practices/workload-optimization/kubernetes/)
