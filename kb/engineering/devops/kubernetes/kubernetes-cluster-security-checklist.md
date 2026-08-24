---
type: checklist
title: Kubernetes cluster security checklist
description: Checks for enforced Kubernetes cluster security controls.
tags:
  - devops
  - kubernetes
  - cluster
  - security
---

# Kubernetes cluster security checklist

Use this checklist when you configure or review Kubernetes cluster security controls.

Apply controls that the cluster operator owns. For managed clusters, confirm the provider responsibility boundary.

## Admission and policy enforcement

- [ ] Enforce the Restricted Pod Security Standard for workload namespaces with Pod Security Admission.
- [ ] Pin the Pod Security Standard version in namespace labels.
- [ ] Use ValidatingAdmissionPolicy or a fail-closed admission webhook to allow images only from approved private registries or registry caches.
- [ ] Apply image-registry checks to `containers`, `initContainers`, and `ephemeralContainers`.
- [ ] Enforce cluster policy before an object is stored, not only in CI.
- [ ] Monitor admission-policy failures and webhook availability.

## Identity and RBAC

- [ ] Authenticate human users through the approved external identity provider.
- [ ] Do not grant routine users or service accounts `cluster-admin`.
- [ ] Use namespace-scoped `Role` and `RoleBinding` unless cluster scope is required.
- [ ] Do not use wildcard verbs, resources, or API groups unless approved.
- [ ] Restrict permissions to read Secrets and to use `bind`, `escalate`, `impersonate`, and workload-creation permissions.
- [ ] Do not bind untrusted identities to `system:masters`.
- [ ] Review privileged bindings and remove unused bindings on a defined schedule.
- [ ] Use a separate, controlled break-glass role and audit its use.

## API server and control-plane exposure

- [ ] Expose the Kubernetes API only through private networking or approved IP ranges.
- [ ] Require TLS for API access and disable anonymous API-server access.
- [ ] Use the `Node` and `RBAC` authorization modes where the cluster operator configures authorization.
- [ ] Restrict etcd access to control-plane components. Do not expose etcd publicly.
- [ ] Restrict kubelet API access and require authenticated, authorized requests.

## Node hardening

- [ ] Use supported, hardened node operating-system images and patch them within the defined service window.
- [ ] Limit SSH and host-level administrator access to approved operators.
- [ ] Enable `NodeRestriction` admission control where the cluster operator configures it.
- [ ] Use a supported container runtime and keep kubelet, runtime, and node operating-system versions supported.
- [ ] Protect node credentials, bootstrap tokens, and cloud instance credentials from workload access.

## Audit and detection

- [ ] Enable Kubernetes API audit logging with a reviewed audit policy.
- [ ] Send audit records to protected central storage with defined retention.
- [ ] Do not record Secret values or other sensitive request bodies in audit output.
- [ ] Alert on privileged RBAC changes, policy exemptions, failed admission decisions, and break-glass access.
- [ ] Test audit-log retrieval during an incident exercise.

## Secrets and data protection

- [ ] Encrypt Kubernetes API data at rest, including Secrets, with approved key management.
- [ ] Rotate encryption keys and verify re-encryption of existing data.
- [ ] Limit access to Secrets through RBAC and audit Secret reads.
- [ ] Use an approved external secret manager when application secrets require lifecycle management beyond Kubernetes Secrets.
- [ ] Do not place secret values in manifests, Git repositories, audit logs, or diagnostic output.

## Policy exceptions

- [ ] Record each exception with scope, owner, reason, compensating controls, approver, and expiry date.
- [ ] Limit exceptions to explicitly named namespaces, identities, or workloads.
- [ ] Protect namespace labels and admission configuration so workload owners cannot grant themselves an exemption.
- [ ] Review exceptions before expiry and remove expired exceptions.
- [ ] Audit every creation or change of an exception.

## Reference

- [Kubernetes security checklist](https://kubernetes.io/docs/concepts/security/security-checklist/)
- [Admission controllers](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)
- [Validating admission policy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/)
- [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/)
- [RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
- [Kubernetes audit logging](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)
- [Encrypting confidential data at rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
