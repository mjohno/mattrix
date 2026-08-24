---
type: checklist
title: Kubernetes service mesh checklist
description: Checks for secure, reliable, and maintainable Kubernetes service-mesh use.
tags:
  - devops
  - kubernetes
  - service-mesh
  - networking
  - security
---

# Kubernetes service mesh checklist

Use this checklist when you adopt or review a Kubernetes service mesh.

## Mesh scope and necessity

- [ ] Define the required outcome: service identity, traffic control, observability, or cross-cluster communication.
- [ ] Do not mesh a workload unless the selected mesh capability provides a required outcome.
- [ ] Define which namespaces, workloads, ingress paths, egress paths, and external services are in scope.
- [ ] Test workloads that use unusual protocols, direct Pod IP access, or host networking before mesh enrollment.

## Identity and mTLS

- [ ] Give each workload a dedicated Kubernetes ServiceAccount.
- [ ] Enforce authenticated and encrypted traffic between in-scope workloads.
- [ ] Verify actual mTLS coverage. Do not assume proxy injection covers non-meshed workloads, health checks, skipped ports, Ingress, or egress.
- [ ] Define the trust anchor, certificate issuer, rotation owner, expiry alerts, and recovery procedure.
- [ ] Restrict access to mesh identity credentials and issuer secrets.
- [ ] Define identity and trust-boundary rules before enabling multi-cluster traffic.

## Traffic policy and resilience

- [ ] Define explicit routing, authorization, and egress policy for each protected service.
- [ ] Set request timeouts from the service latency and caller budget.
- [ ] Enable retries only for idempotent requests. Set a bounded retry count and time budget.
- [ ] Confirm that retries cannot amplify load during a downstream failure.
- [ ] Configure circuit breaking, outlier detection, or load shedding where a failing dependency can exhaust callers.
- [ ] Validate traffic-shifting and rollback behavior before progressive delivery.

## Observability and operations

- [ ] Export mesh metrics for request rate, errors, latency, retries, mTLS status, and proxy health.
- [ ] Propagate trace context across meshed services where distributed tracing is required.
- [ ] Alert on certificate expiry, control-plane health, proxy resource exhaustion, unexpected plaintext traffic, and error-rate changes.
- [ ] Set CPU and memory requests and limits for mesh proxies separately from application containers.
- [ ] Capacity-test the added proxy latency, connection count, CPU, memory, and telemetry volume at expected peak load.

## Lifecycle and failure handling

- [ ] Verify that the control plane is highly available and has defined failure behavior.
- [ ] Test application behavior during proxy crash, control-plane unavailability, certificate-issuer failure, DNS failure, and mesh-policy rollout failure.
- [ ] Define a supported Kubernetes and mesh-version matrix.
- [ ] Upgrade the control plane, data plane, and workload proxies in the vendor-supported order. Canary and verify each stage.
- [ ] Test rollback and emergency mesh bypass or removal without breaking application traffic.

## Reference

- [Kubernetes service mesh](https://kubernetes.io/docs/concepts/services-networking/service-mesh/)
- [Istio security best practices](https://istio.io/latest/docs/ops/best-practices/security/)
- [Istio traffic-management best practices](https://istio.io/latest/docs/ops/best-practices/traffic-management/)
- [Linkerd automatic mTLS](https://linkerd.io/docs/features/automatic-mtls/)
- [Linkerd retries and timeouts](https://linkerd.io/docs/features/retries-and-timeouts/)
- [Istio upgrade guide](https://istio.io/latest/docs/setup/upgrade/)
