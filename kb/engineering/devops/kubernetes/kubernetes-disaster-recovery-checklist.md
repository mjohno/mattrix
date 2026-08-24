---
type: checklist
title: Kubernetes disaster-recovery checklist
description: Checks for tested Kubernetes workload, cluster, and regional recovery.
tags:
  - devops
  - kubernetes
  - disaster-recovery
  - backup
---

# Kubernetes disaster-recovery checklist

Use this checklist when you define or review Kubernetes disaster recovery.

## Recovery objectives and scope

- [ ] Define and approve an RTO and RPO for each critical service and data store.
- [ ] Identify dependencies, owners, recovery order, and service acceptance checks.
- [ ] Define the disaster scenarios covered: namespace loss, cluster loss, region loss, registry loss, and identity-provider loss.
- [ ] Confirm that backup frequency and retention meet each workload's RPO.

## Kubernetes cluster recovery

- [ ] For self-managed control planes, take scheduled etcd snapshots, encrypt them, store them outside the cluster, and verify each snapshot.
- [ ] Keep a tested control-plane rebuild runbook with the Kubernetes, etcd, CNI, CSI, and add-on versions it requires.
- [ ] For managed Kubernetes, document the provider control-plane recovery responsibility and the customer-owned resources that still require backup.
- [ ] Do not rely only on an etcd member data-directory copy. It can omit data still in the write-ahead log.

## Workload and persistent-data recovery

- [ ] Back up required Kubernetes resources, including namespace-scoped configuration, CRDs, and custom resources.
- [ ] Back up persistent volumes with a storage-provider-supported method.
- [ ] Define application-consistent backup and restore procedures for databases and other transactional services.
- [ ] Encrypt backups and restrict backup-store access with least privilege.
- [ ] Store a copy in a separate failure domain, such as another account, project, region, or provider.

## GitOps and supply dependencies

- [ ] Keep declarative cluster and workload configuration in a protected Git repository.
- [ ] Ensure a new cluster can bootstrap Argo CD and reconcile the required desired state from Git.
- [ ] Back up Argo CD application data and document its restore procedure.
- [ ] Preserve access to immutable images, Helm charts, and other deployment artifacts during a regional recovery.

## Access and regional recovery

- [ ] Document break-glass access that does not depend on the failed cluster or its normal identity path.
- [ ] Test recovery of backup encryption keys, secrets, DNS, certificates, registry access, and cloud IAM permissions.
- [ ] Define a tested regional-failover procedure, including traffic routing and prevention of split-brain writes.
- [ ] Define how to restore or recreate external backing services before workloads are started.

## Validation

- [ ] Restore representative workloads and data into an isolated environment on a scheduled basis.
- [ ] Measure the achieved RTO and recovered-data point against the approved RPO.
- [ ] Verify restored applications, data integrity, permissions, network policy, and traffic routing.
- [ ] Record recovery-test results, failures, and required runbook changes.
- [ ] Run a full cluster- or region-loss exercise at a defined interval.

## Reference

- [Kubernetes: Operating etcd clusters](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/)
- [etcd: Disaster recovery](https://etcd.io/docs/v3.5/op-guide/recovery/)
- [Kubernetes: Volume Snapshots](https://kubernetes.io/docs/concepts/storage/volume-snapshots/)
- [Argo CD: Disaster Recovery](https://argo-cd.readthedocs.io/en/stable/operator-manual/disaster_recovery/)
- [Velero: Disaster recovery](https://velero.io/docs/main/disaster-case/)
