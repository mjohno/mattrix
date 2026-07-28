# Protocol Checklist

## Base Checklist

Inherits all items from [base_checklist.md](base_checklist.md). Apply base items before these protocol-specific items. Use this checklist for `metadata.type: protocol` only.

## Protocol-Specific CRITICAL

- [ ] **CRITICAL** `metadata.type: protocol`
- [ ] **CRITICAL** `metadata.category: map`
- [ ] **CRITICAL** `disable_model_invocation: true` is present in frontmatter
- [ ] **CRITICAL** Under `# [Name]`: Goal (mandatory), Non-Goals (mandatory), Use-When (mandatory)
- [ ] **CRITICAL** Section 0: Prerequisites present
- [ ] **CRITICAL** Section 1: Protocol Interface present and identifies the authoritative interface for operating the protocol
- [ ] **CRITICAL** Section 2: Invariants present and includes approval, ordering, state, safety, or transition rules that cannot be violated
- [ ] **CRITICAL** Section 3: Outputs present
- [ ] **CRITICAL** Section 4: Next Steps present
- [ ] **CRITICAL** Section 5: Examples present (at least one)
- [ ] **CRITICAL** Protocol does not require agents to mutate protocol state outside the authoritative interface

## Protocol-Specific QUALITY

- [ ] **QUALITY** Protocol describes one governed interaction pattern, not a general-purpose workflow collection
- [ ] **QUALITY** Primary operation path is discoverable from the authoritative interface or compact instructions
- [ ] **QUALITY** Skill prose is an adapter to the protocol interface, not a duplicate implementation manual
- [ ] **QUALITY** State ownership is explicit and avoids sidecar state unless necessary
- [ ] **QUALITY** Human decision gates and agent action boundaries are unambiguous
- [ ] **QUALITY** Protocol package is human/orchestrator-loaded and does not rely on direct model invocation
- [ ] **QUALITY** Escape hatches, if any, are clearly secondary to the primary protocol path

## Definition of Done

A protocol passes compliance if all base CRITICAL items and all protocol-specific CRITICAL items pass. A beautifully simple protocol also passes all QUALITY items.
