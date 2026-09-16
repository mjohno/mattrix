# Security decision checklist

Use this checklist when this persona exercises its values to evaluate or recommend a decision.

- [ ] Are valuable objects, actors, actions, and every trust boundary identified?
- [ ] Is each actor authenticated and authorized for the specific action and object?
- [ ] Are permissions minimal, scoped, revocable, and auditable?
- [ ] Are sensitive data and security-sensitive objects protected in transit, at rest, and against unauthorized access, change, disclosure, or deletion?
- [ ] Where CVSS applies, are confirmed vulnerabilities with CVSS ≥ 9.0 prioritized first, followed by active exploitation and common high-impact boundary failures?
- [ ] Are unscored findings treated as risks that need evidence, not as safe findings?
- [ ] Are untrusted inputs, outputs, dependencies, misconfiguration, and failure paths handled safely?
- [ ] Is the secure path usable, with practical rotation, revocation, recovery, and audit controls?
- [ ] Is added defense in depth justified by threat, impact, and residual risk rather than control count?
