# Interface Checklist

## Base Checklist

Inherits all items from [base_checklist.md](base_checklist.md). Apply base items before these interface-specific items. Use this checklist for `metadata.type: interface` only; use [communications_checklist.md](communications_checklist.md) for `metadata.type: communications`.

## Interface-Specific CRITICAL

- [ ] **CRITICAL** `metadata.type: interface`
- [ ] **CRITICAL** `metadata.category: interface`
- [ ] **CRITICAL** Under `# [Name]`: Goal (mandatory), Non-Goals (mandatory), Use-When (mandatory)
- [ ] **CRITICAL** Selection rules identify the default minimal contract reference(s)/asset(s).
- [ ] **CRITICAL** Optional references/assets are selected only from explicit caller intent, domain, or constraints.
- [ ] **CRITICAL** Context-loading instructions identify selected package-local paths relative to the interface `SKILL.md`.
- [ ] **CRITICAL** Context-loading instructions require selected references/assets to be loaded without emitting their contents in chat.
- [ ] **CRITICAL** Includes one minimal example with a prompt and a direct-invocation loaded-path acknowledgement.
- [ ] **CRITICAL** Interface defines contract data only and does not create, modify, evaluate, persist, retrieve external data, or orchestrate work.

## Interface-Specific QUALITY

- [ ] **QUALITY** Interface defines a noun/domain desired state, not production behavior.
- [ ] **QUALITY** Interface exposes conventions, quality checks, templates, schemas, protocol rules, artifact shapes, or storage rules for consumers.
- [ ] **QUALITY** Default selection loads exactly one compact contract file when possible.
- [ ] **QUALITY** Generic rules are separated from language/platform-specific or intent-specific details when domains exist.
- [ ] **QUALITY** Optional references/assets are clearly named by use, e.g. `[domain]_contract.md`, `[artifact]_checklist.md`, or `[artifact]_quality.md`.
- [ ] **QUALITY** Templates are examples or canonical shapes consumed by verb skills, not mandatory generation behavior unless explicitly stated.
- [ ] **QUALITY** Minimal default output is no interface-only response when composed, or selected paths only for a direct interface invocation.
- [ ] **QUALITY** Missing or unsupported domains are stated as assumptions/unknowns with a concrete handoff.
- [ ] **QUALITY** The minimal example is short and does not duplicate the full contract.

## Definition of Done

An interface passes compliance if all base CRITICAL items and all interface-specific CRITICAL items pass. A beautifully simple interface also passes all QUALITY items.
