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

Unknown types are allowed; consumers should tolerate them.

## Manual Bundle Discovery Information

MKF bundle selectors may be explicit filesystem paths or configured bundle names.

Environment convention:

```sh
MKF_BUNDLES=GENERAL;PHOENIX;MY-BUNDLE;
MKF_GENERAL_BUNDLE=/knowledge/general
MKF_PHOENIX_BUNDLE=/knowledge/phoenix
MKF_MY_BUNDLE_BUNDLE=/knowledge/my-bundle
```

Manual interpretation:
- `MKF_BUNDLES` is semicolon-delimited.
- Trim whitespace and ignore empty entries.
- Normalize selector names to uppercase.
- Treat `-` and `_` as equivalent for environment variable lookup.
- Resolve normalized names through `MKF_<NAME>_BUNDLE`.
- Explicit filesystem paths can be used directly as bundle roots when valid.

Resolved bundle record shape:

```yaml
name: GENERAL
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
