---
type: checklist
title: Kubernetes stateful workload checklist
description: Checks for safe, reliable Kubernetes workloads with persistent state.
tags:
  - devops
  - kubernetes
  - statefulset
  - storage
---

# Kubernetes stateful workload checklist

Use this checklist when you create or review a Kubernetes workload with persistent state.

## StatefulSet design

- [ ] Use a `StatefulSet` only when stable Pod identity or persistent per-replica storage is required.
- [ ] Set `serviceName` to a headless Service that provides stable network identity.
- [ ] Use `volumeClaimTemplates` so each replica receives its own PersistentVolumeClaim.
- [ ] Confirm that the application can recover when a Pod restarts with its existing volume.
- [ ] Configure a PodDisruptionBudget that preserves the application quorum.

## Persistent storage

- [ ] Select a StorageClass with the required availability, performance, encryption, expansion, and topology properties.
- [ ] Set access modes that match the application write model. Do not allow multiple writers unless the application and storage support them.
- [ ] Use `WaitForFirstConsumer` volume binding when storage topology must follow Pod scheduling.
- [ ] Define `persistentVolumeClaimRetentionPolicy` explicitly for scale-down and StatefulSet deletion.
- [ ] Monitor PersistentVolumeClaim capacity and define a volume-expansion procedure before capacity is exhausted.
- [ ] Do not store durable data on `emptyDir`, container writable layers, or node-local paths unless data loss is acceptable.

## Lifecycle and rollout

- [ ] Use `OrderedReady` unless the application is proven safe to start and stop in parallel.
- [ ] Configure `Parallel` Pod management only when bootstrap, membership, and recovery are safe under concurrent operations.
- [ ] Use rolling updates with a partition for staged StatefulSet changes.
- [ ] Confirm that upgrades, rollback, and image changes preserve schema and on-disk data compatibility.
- [ ] Set termination grace time and shutdown handling so the application can flush or transfer data safely.
- [ ] Test a failed or stalled rollout and its recovery procedure.

## Backup and restore

- [ ] Define backups for every persistent data volume and required dependent metadata, configuration, keys, and credentials.
- [ ] Use a snapshot or backup mechanism supported by the selected CSI driver and StorageClass.
- [ ] Define backup frequency, retention, encryption, access control, and an owner for backup failures.
- [ ] Coordinate backups with the application to achieve its required consistency level.
- [ ] Define the recovery order for multi-volume, replicated, or database workloads.
- [ ] Test restore regularly in an isolated environment from a real backup.
- [ ] Verify restored application health, data integrity, membership, recovery point, and recovery time.
- [ ] Prevent a restored replica from joining or writing to the production cluster during testing.

## Data consistency and failure recovery

- [ ] Define the consistency model, quorum, and failure behavior for the application.
- [ ] Confirm that the application handles duplicate requests, interrupted writes, and abrupt node or Pod loss.
- [ ] Test simultaneous storage unavailability and Pod rescheduling.
- [ ] Define safe procedures for replacing a failed replica, scaling down, and deleting orphaned PersistentVolumeClaims.
- [ ] Alert on failed backups, PersistentVolumeClaim exhaustion, replica health, replication lag, and failed recovery jobs.

## Reference

- [Kubernetes StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)
- [Volume Snapshots](https://kubernetes.io/docs/concepts/storage/volume-snapshots/)
- [Pod Disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)
- [PodDisruptionBudgets](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)
