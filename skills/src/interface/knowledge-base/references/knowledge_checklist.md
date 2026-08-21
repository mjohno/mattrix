# Knowledge Checklist

Use this for MKF and OKF v0.2 conformance checks. A concept or bundle passes when every applicable critical item passes.

## Concept Critical

- [ ] Concept is a non-reserved Markdown file with a parseable YAML frontmatter mapping.
- [ ] Frontmatter includes a non-empty string `type`.
- [ ] Unknown frontmatter keys are preserved on update.

## Reserved File Critical

- [ ] An `index.md`, when present, is not treated as a concept and uses the OKF index structure.
- [ ] A `log.md`, when present, is not treated as a concept and uses ISO `YYYY-MM-DD` date headings.

## Bundle Critical

- [ ] Bundle root is a filesystem directory tree.
- [ ] Bundle selection resolves from an explicit path or an unambiguous `MKF_PATH` root basename.

## Advanced OKF Advisories

- [ ] `tags`, when present, is a list.
- [ ] Each `sources` entry, when present, has a `resource`.
- [ ] `generated`, `verified`, lifecycle, and computation fields use their applicable OKF v0.2 shapes.

## Boundary Critical

- [ ] Search and ranking are handled by `input/lookup`, not the knowledge interface.
- [ ] Writes, validation, and explicitly requested index rebuilding are handled by `output/record`, not the knowledge interface.

## Quality

A failed Quality item produces a `Partial` result. It does not fail conformance.

- [ ] Each concept focuses on one durable idea or reusable artifact.
- [ ] Each concept has a non-empty description that supports selection during lookup.
- [ ] Titles and descriptions, when present, are clear and specific.
- [ ] Tags, when present, improve retrieval without becoming noisy.
- [ ] Citations or keyed source footnotes are present where claims need attribution.
- [ ] Indexes are clearly separate from authored concepts and useful for progressive disclosure.
- [ ] Manual bundle discovery can be understood from visible environment or path information.
- [ ] Lookup and search behaviors are kept out of passive knowledge contract material.
- [ ] Write, update, and index-rebuild behaviors are kept in record tooling.
- [ ] Advanced OKF fields, when present, provide provenance, trust, lifecycle, and attestation metadata that supports informed consumer judgment.
