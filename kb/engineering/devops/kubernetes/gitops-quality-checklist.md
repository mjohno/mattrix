---
type: checklist
title: GitOps quality checklist
description: Checks for a secure, reliable, and auditable GitOps delivery process.
tags:
  - devops
  - kubernetes
  - gitops
  - argocd
  - delivery
---

# GitOps quality checklist

Use this checklist when you create or review a GitOps delivery process.

## Desired state

- [ ] Store the desired state for each managed environment in Git.
- [ ] Use declarative manifests, Helm releases, or Kustomize definitions.
- [ ] Do not make manual production changes outside the GitOps process.
- [ ] Record approved exceptions and reconcile them back into Git.
- [ ] Keep application code and deployment configuration in separate repositories when their access controls or release cycles differ.

## Repository structure

- [ ] Make environment, application, component, and owner boundaries clear in the repository structure.
- [ ] Keep each environment definition independent and easy to locate.
- [ ] Use shared base definitions only when their ownership and versioning are clear.
- [ ] Keep environment-specific values small and explicit.
- [ ] Do not duplicate secrets or configuration across unrelated environments.

## Change control

- [ ] Require pull-request review before changes reach a protected environment.
- [ ] Require automated manifest validation before merge.
- [ ] Require policy and security checks before merge.
- [ ] Protect the default branch and environment branches from direct changes.
- [ ] Sign commits or verify their origin where the platform supports it.
- [ ] Link each production change to its review and change record.

## Reconciliation

- [ ] Use Argo CD to pull desired state from Git.
- [ ] Define an Argo CD Application for each managed deployment boundary.
- [ ] Configure the Argo CD sync policy and sync options explicitly.
- [ ] Set a suitable reconciliation interval for each environment.
- [ ] Detect and report drift from the declared state.
- [ ] Correct drift automatically only when the workload and environment allow it.
- [ ] Limit the controller permissions to the namespaces and resources it must manage.
- [ ] Keep controller credentials and access tokens in a secure secret store.

## Promotion and release

- [ ] Promote the same tested artifact between environments.
- [ ] Use immutable image tags or digests in deployment configuration.
- [ ] Make the promotion path from development to production explicit.
- [ ] Require approval before a production promotion when required by policy.
- [ ] Record the deployed Git revision, manifest revision, and image digest.
- [ ] Define and test a rollback process that reverts to a known good Git revision.

## Secrets and supply chain

- [ ] Do not store plaintext secrets in Git.
- [ ] Encrypt secrets in Git or retrieve them from an approved external secret manager.
- [ ] Limit read access to repositories that contain deployment configuration.
- [ ] Scan images and manifests for known vulnerabilities and insecure settings.
- [ ] Verify image provenance or signatures when the platform supports it.
- [ ] Generate or retain an SBOM when required by policy.

## Operations

- [ ] Alert when reconciliation fails, drift persists, or a deployment is unhealthy.
- [ ] Retain controller logs and deployment history for investigation.
- [ ] Monitor controller health, queue depth, and reconciliation latency.
- [ ] Back up Git repositories, controller configuration, and secret-management data.
- [ ] Test recovery when the GitOps controller or target cluster is unavailable.

## Reference

- [OpenGitOps Principles](https://opengitops.dev/)
- [Argo CD documentation](https://argo-cd.readthedocs.io/)
