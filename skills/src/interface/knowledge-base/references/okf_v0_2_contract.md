# OKF v0.2 Contract

This reference summarizes the broader Open Knowledge Format v0.2 contract. MKF consumers read and preserve these optional families; record authors them only on explicit request.

## Core Structure

A concept is a UTF-8 Markdown file with YAML frontmatter and a Markdown body. `type` is the only required frontmatter key. Consumers tolerate unknown types, unknown keys, broken links, and absent optional metadata.

Concept links may be bundle-relative (`/path.md`) or relative. `index.md` and `log.md` are optional reserved files, not concepts. An index groups Markdown links under headings. A log groups prose entries under ISO `YYYY-MM-DD` headings.

## Optional Metadata

- `title`, `description`, `resource`, and `tags` provide presentation and retrieval metadata.
- `sources` records provenance. Each source entry requires `resource`; keyed body footnotes may use a source `id`.
- `generated: { by, at }` records production. `verified` records one mapping or a list of `{ by, at }` verification events.
- `status` is `draft`, `stable`, or `deprecated`; absent means `stable`. `stale_after` is an absolute `YYYY-MM-DD` date.
- Actors use `<producer>/<version>`, `human:<id>`, or `process:<id>`.

## Attested Computation

A `type: Attested Computation` concept may declare `runtime`, typed `parameters`, optional `computation`, `executor`, and `attester`. It records a sanctioned computation; OKF does not execute or attest it.

## Version

The upstream contract is Open Knowledge Format v0.2. A bundle-root `index.md` may declare `okf_version: "0.2"`; MKF index rebuilding ignores that declaration.
