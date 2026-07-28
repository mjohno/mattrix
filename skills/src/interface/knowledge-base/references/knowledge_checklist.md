# Knowledge Checklist

Use this for MKF conformance checks. A concept or bundle passes when every applicable critical item passes.

## Concept Critical

- [ ] Concept is a Markdown file with YAML frontmatter.
- [ ] Frontmatter includes `type`, `title`, `description`, and `tags`.
- [ ] `tags` is a list; `tags: []` is valid.
- [ ] Concept ID is the bundle-relative path without `.md`.
- [ ] Unknown frontmatter keys are preserved on update.
- [ ] Source-backed claims include citations when needed.

## Bundle Critical

- [ ] Bundle root is a filesystem directory tree.
- [ ] `index.md` concepts use `type: index` when generated.
- [ ] `log.md` is not used as an MKF concept.
- [ ] Bundle selector can be resolved manually from explicit path or `MKF_BUNDLES`/`MKF_<NAME>_BUNDLE` information.

## Boundary Critical

- [ ] Search/ranking behavior is handled by `input/lookup`, not the knowledge interface.
- [ ] Writes, validation scripts, and index rebuilds are handled by `output/record`, not the knowledge interface.
