---
type: checklist
title: Kubernetes network ingress and TLS checklist
description: Checks for secure network policy, ingress exposure, TLS, and service discovery.
tags:
  - devops
  - kubernetes
  - networking
  - ingress
  - tls
---

# Kubernetes network ingress and TLS checklist

Use this checklist when you expose or connect Kubernetes workloads.

For basic NetworkPolicy and TLS rules, use the [Kubernetes workload quality checklist](kubernetes-workload-quality-checklist.md).

## NetworkPolicy enforcement

- [ ] Verify that the cluster CNI enforces `NetworkPolicy`.
- [ ] Test that default-deny ingress and egress policies block traffic as intended.
- [ ] Allow DNS egress explicitly from workloads that require DNS resolution.
- [ ] Define egress rules for each approved external dependency, destination, port, and protocol.
- [ ] Do not assume native `NetworkPolicy` can filter by FQDN, inspect TLS, log denied traffic, or create explicit deny rules.
- [ ] Use an approved CNI, proxy, or service-mesh control when FQDN policy, layer-7 policy, or network-event logging is required.
- [ ] Account for NetworkPolicy propagation during Pod startup and policy changes.

## Ingress exposure

- [ ] Use an explicitly selected, approved `IngressClass`.
- [ ] Confirm that an Ingress controller exists; an Ingress object alone does not expose an application.
- [ ] Define exact hostnames and paths. Do not use broad wildcard hosts unless approved.
- [ ] Use the correct `pathType` for each route and test route matching.
- [ ] Expose only required HTTP and HTTPS services through Ingress.
- [ ] Keep administration, metrics, and internal service endpoints off public Ingress unless explicitly approved.
- [ ] Define a controller-specific request-size limit, timeout, retry policy, and rate limit for each exposed application.
- [ ] Test that error responses do not disclose internal upstream names, addresses, or credentials.

## TLS and certificates

- [ ] Define TLS for every public hostname and redirect HTTP to HTTPS.
- [ ] Verify that every TLS certificate covers its configured hostname.
- [ ] Store the certificate and private key in a protected TLS Secret with `tls.crt` and `tls.key`.
- [ ] Automate certificate issuance and renewal. Alert before expiry and on failed renewal.
- [ ] Rotate private keys according to the selected certificate-manager policy.
- [ ] Define the minimum TLS version and permitted cipher suites in the selected Ingress controller.
- [ ] Encrypt traffic from the Ingress controller to the backend when that hop crosses a trust boundary or policy requires it.
- [ ] Restrict who can read or modify TLS Secrets and Ingress configuration.

## DNS and service discovery

- [ ] Use Service DNS names instead of Pod IP addresses.
- [ ] Use namespace-qualified Service names for cross-namespace dependencies.
- [ ] Use the Service FQDN where ambiguity or custom DNS search domains can cause misrouting.
- [ ] Test DNS resolution under the workload's actual `dnsPolicy` and NetworkPolicy rules.
- [ ] Avoid DNS names that resolve differently by namespace unless this is intentional and documented.

## Validation and operations

- [ ] Test allowed and denied ingress and egress paths from the deployed namespace.
- [ ] Test certificate renewal, hostname mismatch handling, HTTP-to-HTTPS redirects, and backend TLS behavior.
- [ ] Test timeout, retry, and rate-limit behavior against expected client load and failure conditions.
- [ ] Monitor Ingress-controller errors, TLS-renewal failures, DNS failures, and rejected network traffic where the platform supports it.

## Reference

- [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [Kubernetes DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- [cert-manager Certificate resource](https://cert-manager.io/docs/usage/certificate/)
