---
type: checklist
title: Kubernetes workload quality checklist
description: Checks for secure, reliable, and maintainable Kubernetes workloads.
tags:
  - devops
  - kubernetes
  - containers
  - workloads
---

# Kubernetes workload quality checklist

Use this checklist when you create or review a Kubernetes workload.

## Workload definition

- [ ] Use the correct workload type: `Deployment`, `StatefulSet`, `DaemonSet`, `Job`, or `CronJob`.
- [ ] Use consistent labels for application, component, version, and owner.
- [ ] Use an immutable container image tag or digest.
- [ ] Do not use the `latest` image tag.
- [ ] Set the required replica count and rollout strategy.

## Container images

- [ ] Pull images only from approved private registries or approved registry caches.
- [ ] Do not pull images directly from public registries such as Docker Hub.
- [ ] Use repository access controls and image-pull credentials.
- [ ] Use immutable image tags or digests.

## Resources and health

- [ ] Set CPU and memory requests for every container.
- [ ] Set CPU and memory limits where they are appropriate.
- [ ] Set ephemeral-storage requests and limits when the workload uses local storage.
- [ ] Configure a readiness probe before sending traffic to a Pod.
- [ ] Configure a liveness probe only when it can detect an unrecoverable failure.
- [ ] Configure a startup probe for slow-starting applications.
- [ ] Set probe timeouts and failure thresholds for expected application behavior.

## Configuration and state

- [ ] Keep configuration outside the container image.
- [ ] Use ConfigMaps for non-sensitive configuration.
- [ ] Use Secrets for credentials and sensitive configuration.
- [ ] Do not put secrets in image layers, manifests, command arguments, or logs.
- [ ] Keep persistent state in an external backing service or a declared persistent volume.
- [ ] Do not depend on Pod-local files or memory for durable state.

## Pod security

- [ ] Apply the Restricted Pod Security Standard unless an exception is approved.
- [ ] Run containers as a non-root user.
- [ ] Set `allowPrivilegeEscalation: false`.
- [ ] Drop all Linux capabilities and add only required capabilities.
- [ ] Use the `RuntimeDefault` seccomp profile.
- [ ] Use a read-only root filesystem when practical.
- [ ] Do not use privileged containers, host networking, host PID, host IPC, or host-path volumes unless required.
- [ ] Mount the service-account token only when the workload needs Kubernetes API access.
- [ ] Give the workload only the required RBAC permissions.

## Network

- [ ] Define ingress and egress NetworkPolicies.
- [ ] Start from default-deny policy rules and add only required traffic.
- [ ] Permit only required ports, protocols, namespaces, and services.
- [ ] Use TLS for traffic that crosses a trust boundary.

## Availability and rollout

- [ ] Run more than one replica when the service needs high availability.
- [ ] Add a PodDisruptionBudget when voluntary disruptions could reduce availability.
- [ ] Configure graceful shutdown and a suitable termination grace period.
- [ ] Set rollout progress and rollback controls.
- [ ] Confirm that a failed rollout can be detected and reversed.

## Observability and validation

- [ ] Send application logs to `stderr`.
- [ ] Export health, metrics, and traces where the service requires them.
- [ ] Validate manifests before deployment.
- [ ] Check manifests against policy controls before deployment.
- [ ] Test the workload with the target Kubernetes version and admission policies.

## Reference

- [Kubernetes security checklist](https://kubernetes.io/docs/concepts/security/security-checklist/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Liveness, readiness, and startup probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/)
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
