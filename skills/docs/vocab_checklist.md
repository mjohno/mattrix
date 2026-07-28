# Vocab Checklist

## Base Checklist

Inherits applicable items from [base_checklist.md](base_checklist.md), except where vocabulary-specific rules intentionally differ. Use this checklist for `metadata.type: vocabulary` with `metadata.category: interface` only.

## Vocab-Specific CRITICAL

- [ ] **CRITICAL** `metadata.type: vocabulary`
- [ ] **CRITICAL** `metadata.category: interface`
- [ ] **CRITICAL** `disable_model_invocations: true` is present in frontmatter
- [ ] **CRITICAL** Description includes "Use when..." triggers and names the terms defined, e.g. `Use when terms like study, lean need definition.`
- [ ] **CRITICAL** Frontmatter does not include a separate term list or extra vocabulary metadata
- [ ] **CRITICAL** Under `# vocab`: Goal, Non-Goals, and Terms sections are present
- [ ] **CRITICAL** Terms may include lightweight behavioral controls that clarify user intent, but must not define multi-step workflows, required inputs, formal outputs, verification criteria, or tool-specific procedures
- [ ] **CRITICAL** No term duplicates an existing skill package name
- [ ] **CRITICAL** No term restates or competes with a meaning already defined by an existing skill description
- [ ] **CRITICAL** Vocab package is context-only and contains no Selection, Return, Inputs, Processes, Outputs, Next Steps, or Examples sections

## Vocab-Specific QUALITY

- [ ] **QUALITY** Each term has one concise operational meaning
- [ ] **QUALITY** Terms are non-overlapping with each other
- [ ] **QUALITY** Terms are not synonyms for existing specialized skills; prefer updating that skill description instead
- [ ] **QUALITY** Terms are stable project vocabulary, not one-off prompt preferences
- [ ] **QUALITY** Definitions may constrain default agent behavior, but remain compact intent semantics rather than full skill processes
- [ ] **QUALITY** Definitions avoid circular references to other vocab terms unless the relationship is explicitly clarifying
- [ ] **QUALITY** Definitions avoid references to the vocab package itself; consuming prompts should not need to say "see vocab"
- [ ] **QUALITY** Domain-specific terminology is kept in the relevant knowledge-base glossary, not project vocab
- [ ] **QUALITY** Default loaded content is compact enough to fit comfortably in context before a first prompt

## Overlap Check

Before adding or changing a term:

1. List existing skill names under `../src/*/*/SKILL.md`.
2. Search skill descriptions and `Use-When` lines for the proposed term.
3. If the term matches a skill name, reject it from vocab.
4. If the term is already substantively defined by a skill description, update that skill instead of adding a vocab term.
5. If the term is domain-local, place it in the knowledge-base glossary instead of project vocab.

## Definition of Done

A vocab package passes compliance if all applicable base CRITICAL items and all vocab-specific CRITICAL items pass. A beautifully simple vocab package also passes all QUALITY items.
