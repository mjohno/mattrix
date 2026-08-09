# Communications Checklist

## Base Checklist

Inherits applicable items from [base_checklist.md](base_checklist.md). Use this checklist only for `metadata.type: communications` with `metadata.category: interface`.

## Communications-Specific CRITICAL

- [ ] **CRITICAL** `metadata.type: communications`
- [ ] **CRITICAL** `metadata.category: interface`
- [ ] **CRITICAL** `disable_model_invocations: true` is present in frontmatter
- [ ] **CRITICAL** Description includes a "Use when..." trigger for user-loaded communication control
- [ ] **CRITICAL** Under `# [Name]`: Goal, Non-Goals, Application, and Controls sections are present
- [ ] **CRITICAL** Application states user activation, communication scope, applicable exact-text exclusions, and higher-priority instruction precedence
- [ ] **CRITICAL** Controls are compact declarative communication rules
- [ ] **CRITICAL** Package is context-only and contains no Selection, Return, Inputs, Processes, Outputs, Next Steps, Examples, or tool-specific procedures
- [ ] **CRITICAL** Package does not define an artifact schema, required response fields, verification criteria, or a multi-step workflow

## Communications-Specific QUALITY

- [ ] **QUALITY** The package has one stable communication purpose
- [ ] **QUALITY** Controls are concise and non-overlapping
- [ ] **QUALITY** The package clearly limits the content or channels it controls
- [ ] **QUALITY** Package-specific sections clarify the control without adding a workflow
- [ ] **QUALITY** Terms do not duplicate existing skill package names or meanings owned by skill descriptions
- [ ] **QUALITY** Domain-local terminology remains in the relevant knowledge-base glossary
- [ ] **QUALITY** Default loaded content is compact enough to fit comfortably in context before a first prompt

## Definition of Done

A communications package passes compliance if all applicable base CRITICAL items and all communications-specific CRITICAL items pass. A beautifully simple communications package also passes all QUALITY items.
