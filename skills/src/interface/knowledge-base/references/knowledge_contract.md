# Knowledge Contract

Matt's Knowledge Format (MKF) is a filesystem bundle of Markdown concept documents with YAML frontmatter. MKF should remain compatible with Google OKF v0.1 unless a future explicit decision changes this contract.

## Bundle Structure

```text
bundle-root/
├── index.md
├── concept.md
└── group/
    ├── index.md
    └── nested-concept.md
```

- A bundle is a filesystem directory tree.
- Concepts are Markdown files with YAML frontmatter.
- Concept ID is the bundle-relative file path without `.md`.
- `index.md` is a generated concept with `type: index`.
- `log.md` is avoided in MKF.

## Required Frontmatter

```yaml
---
type: undefined
title: Example Concept
description: A short description.
tags: []
---
```

Required fields: `type`, `title`, `description`, `tags`.

Rules:
- `tags: []` is valid.
- `resource` is optional.
- `timestamp` is not required and should not be auto-maintained.
- Unknown frontmatter keys are allowed and should be preserved on update.

## Known Types

- `undefined`: free-form Markdown; include `# Citations` only when citations exist.
- `index`: generated directory listing for progressive disclosure.
- `checklist`: quality checklist for reviews.
- `template`: reusable LLM/agent processing template.
- `adr`: supporting detail for an architecture decision registered in an `adr-index` concept.
- `adr-index`: source-of-truth registry of architecture decisions.

Unknown types are allowed; consumers should tolerate them.

## Bundle Discovery Information

Configured bundles are supplied through `MKF_PATH`, a colon-delimited list of bundle-root paths:

```sh
MKF_PATH=/knowledge/general:/knowledge/phoenix:/knowledge/my-bundle
```

Manual interpretation:
- Split `MKF_PATH` on `:`.
- Trim whitespace and ignore empty entries, including repeated or trailing separators.
- Expand `~` and resolve each remaining entry as a filesystem bundle root.
- Preserve root order; consumers search earlier roots before later roots.
- Derive a bundle's display label from its root directory basename.
- Explicit filesystem paths may be used directly as one-off bundle roots when valid; they do not require membership in `MKF_PATH`.
- A basename selector is valid only when it identifies exactly one configured root. Consumers must report duplicate basenames as ambiguous rather than choosing one.

Resolved bundle record shape:

```yaml
name: general
root: /knowledge/general
source: env | prompt-path
```

## Boundaries

- Operational bundle discovery, search order, ranking, and match loading belong to `input/lookup`.
- Writing, duplicate handling, validation scripts, templates, and index rebuilding belong to `output/record`.
- This interface defines passive MKF shape and manual discovery information only.

## Minimal Example

```text
Concept ID: quality/skill-checklist
Path: <bundle-root>/quality/skill-checklist.md
Frontmatter: type, title, description, tags
Body: Markdown concept content
```
