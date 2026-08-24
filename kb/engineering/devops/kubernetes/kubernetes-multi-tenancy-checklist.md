---
type: checklist
title: Kubernetes multi-tenancy checklist
description: Checks for enforced Kubernetes tenant boundaries.
tags:
  - devops
  - kubernetes
  - multi-tenancy
  - security
---

# Kubernetes multi-tenancy checklist

Use this checklist when you set or review Kubernetes tenant boundaries.

A namespace is a soft boundary. Use separate clusters when tenants require hard security isolation.

## Tenant boundary and namespaces

- [ ] Define each tenant, its trust level, its owner, and its approved namespaces.
- [ ] Use separate namespaces for separate soft tenants.
- [ ] Label namespaces with tenant, owner, environment, and data-classification values.
- [ ] Define an approved namespace creation, transfer, and deletion process.
- [ ] Prevent tenants from changing boundary-control resources in their namespaces unless explicitly approved.

## Access control

- [ ] Use namespace-scoped `Role` and `RoleBinding` objects for tenant access.
- [ ] Give each user, group, and service account only required permissions.
- [ ] Do not give tenants `cluster-admin` or uncontrolled `ClusterRoleBinding` access.
- [ ] Do not grant wildcard verbs, resources, or API groups.
- [ ] Do not grant `escalate`, `bind`, or `impersonate` permissions unless an approved administrator needs them.
- [ ] Restrict `get`, `list`, and `watch` access to Secrets.
- [ ] Use separate service accounts for separate workloads. Do not automatically mount API tokens unless required.
- [ ] Review tenant RBAC bindings and service accounts at a defined interval.

## Resource isolation

- [ ] Apply a `ResourceQuota` to every tenant namespace.
- [ ] Set CPU, memory, ephemeral-storage, object-count, and persistent-volume quotas as applicable.
- [ ] Apply a `LimitRange` with approved default, minimum, and maximum resource values.
- [ ] Prevent a tenant from removing or weakening its quota or limit controls.
- [ ] Define a reviewed process for quota increases and temporary exceptions.

## Network isolation

- [ ] Confirm that the cluster network plugin enforces `NetworkPolicy`.
- [ ] Apply default-deny ingress and egress policies in every tenant namespace.
- [ ] Allow only required DNS, ingress, observability, and backing-service traffic.
- [ ] Allow cross-tenant traffic only through explicit, reviewed policies.
- [ ] Select allowed namespaces and Pods with stable labels, not broad selectors.
- [ ] Review policies after namespace-label or workload-label changes.

## Policy enforcement

- [ ] Enforce the approved Pod Security Admission profile on tenant namespaces.
- [ ] Use admission policy to require tenant labels and required boundary resources.
- [ ] Use admission policy to reject unauthorized image registries, privileged workload settings, and cross-tenant exceptions.
- [ ] Keep policy-controller and platform-administrator namespaces outside tenant control.
- [ ] Record every exception with an owner, reason, scope, and expiry date.

## Audit and assurance

- [ ] Enable Kubernetes API audit logging.
- [ ] Audit authentication, authorization failures, RBAC changes, namespace changes, and boundary-control changes.
- [ ] Protect audit logs from tenant modification and define retention and access controls.
- [ ] Do not record Secret values or other sensitive request bodies in audit logs.
- [ ] Periodically test that one tenant cannot read, modify, exhaust, or connect to another tenant's resources.

## Reference

- [Kubernetes multi-tenancy](https://kubernetes.io/docs/concepts/security/multi-tenancy/)
- [RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
- [Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
- [Limit Ranges](https://kubernetes.io/docs/concepts/policy/limit-range/)
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/)
- [Kubernetes auditing](https://kubernetes.io/docs/concepts/cluster-administration/audit/)
