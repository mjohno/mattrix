---
type: checklist
title: Kubernetes supply-chain checklist
description: Checks for trusted container images and secure Kubernetes supply-chain controls.
tags:
  - devops
  - kubernetes
  - supply-chain
  - containers
  - security
---

# Kubernetes supply-chain checklist

Use this checklist when you build, publish, approve, or deploy container images to Kubernetes.

For basic image-source and image-reference rules, use the [Kubernetes workload quality checklist](kubernetes-workload-quality-checklist.md).

## Approved image supply

- [ ] Mirror approved upstream images into a controlled registry before deployment.
- [ ] Preserve and deploy the upstream image digest when an image is mirrored.
- [ ] Restrict registry write access to approved build identities.
- [ ] Protect approved repositories from unreviewed image publication.
- [ ] Retain image metadata, signatures, attestations, and scan results for each deployed digest.

## Build provenance and signing

- [ ] Build release images through an approved CI build platform from a reviewed source revision.
- [ ] Create signed provenance that identifies the source revision, build platform, and output image digest.
- [ ] Sign each release image and its supply-chain attestations.
- [ ] Verify the image signature, trusted signer identity, trusted issuer or key, and signed image digest before deployment.
- [ ] Store signatures and attestations with, or by immutable reference to, the approved image.

## SBOM and vulnerability management

- [ ] Generate an SBOM for every release image, including operating-system and application dependencies.
- [ ] Store the SBOM with, or by immutable reference to, the release image digest.
- [ ] Scan source dependencies, base images, and final release images for known vulnerabilities.
- [ ] Apply a documented severity, exploitability, and exception policy before release.
- [ ] Record approved vulnerability exceptions with an owner and expiry date.

## Dependency and image updates

- [ ] Define an owner and review interval for application dependencies, base images, and approved upstream images.
- [ ] Rebuild, scan, sign, and publish a new immutable image when an approved dependency or base-image update is required.
- [ ] Test and promote updated images through the normal delivery path.
- [ ] Do not replace an existing image tag.

## Admission enforcement

- [ ] Enforce approved registry, digest, signature, provenance, and vulnerability-policy requirements at admission time.
- [ ] Configure enforcement to reject non-compliant workloads, not only report them.
- [ ] Test admission policy against valid, unsigned, untrusted, mutable-tag, public-registry, and policy-exception cases.
- [ ] Limit, audit, and expire any break-glass exception.

## Secrets and registry credentials

- [ ] Do not store registry credentials, signing keys, or tokens in source code, container images, manifests, command arguments, or logs.
- [ ] Give each build and deployment identity only the registry and signing permissions it needs.
- [ ] Keep image-pull credentials scoped to the required registry and repository access.
- [ ] Encrypt Kubernetes Secrets at rest and restrict Secret read access with RBAC.
- [ ] Rotate and revoke registry credentials and signing keys after exposure, role change, or expiry.

## Reference

- [Kubernetes images](https://kubernetes.io/docs/concepts/containers/images/)
- [Kubernetes admission control](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)
- [Kubernetes Secret good practices](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)
- [Sigstore: verifying signatures](https://docs.sigstore.dev/cosign/verifying/verify/)
- [SLSA security levels](https://slsa.dev/spec/v1.1/levels)
- [CISA: Software Bill of Materials](https://www.cisa.gov/sbom)
