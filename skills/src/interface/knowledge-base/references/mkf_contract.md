# MKF Contract

Matt's Knowledge Format (MKF) is Mattrix's default application of the OKF v0.2 conformance baseline. A bundle is a filesystem directory tree of UTF-8 Markdown files.

## Concepts

Every non-reserved `.md` file is a concept. It must have a parseable YAML frontmatter mapping at the start of the file with a non-empty string `type`.

```yaml
---
type: undefined
---
```

`title`, `description`, `resource`, and `tags` are optional. Unknown types and frontmatter keys are valid and must be preserved during update.

## Reserved Files

`index.md` and `log.md` are reserved non-concept filenames at every directory level. They are optional.

- An `index.md`, when present, is an OKF directory listing. It has no frontmatter, except that a bundle-root index may declare `okf_version`.
- A `log.md`, when present, is an OKF chronological update log with ISO `YYYY-MM-DD` headings.
- MKF consumers support and preserve reserved files. Record does not create logs and rebuilds indexes only on explicit request.

## Discovery

Configured bundles are supplied through `MKF_PATH`, a colon-delimited list of bundle-root paths. Split on `:`, trim whitespace, ignore empty entries, expand `~`, resolve paths, and preserve root order. A root basename selector is valid only when it identifies exactly one configured root. Explicit filesystem paths may be used directly as one-off roots.

## Boundaries

- Bundle discovery, search order, ranking, and concept loading belong to `input/lookup`.
- Writing, duplicate handling, validation, and explicitly requested index rebuilding belong to `output/record`.
- This interface defines passive knowledge shape and discovery information only.
