# MKF Record Process

## Purpose

Create or update one MKF concept safely and validate the shared contract programmatically.

## Write Flow

1. Resolve exactly one target bundle root from an explicit filesystem path or an unambiguous configured `MKF_PATH` root basename.
2. Determine the target concept path and concept ID; reject `index.md` and `log.md` targets.
3. Check likely duplicates by exact path/concept ID and, when present, equal `title` or `resource`.
4. Ask before overwriting, resolving a collision, or making a substantial replacement.
5. Draft or update Markdown while preserving unknown frontmatter keys and existing body content.
6. Add `sources`, trust, lifecycle, or computation metadata only for an explicit advanced-OKF request.
7. Run `scripts/validate_frontmatter.py` on changed concept files.
8. Write only valid concepts.
9. Run `scripts/rebuild_indexes.py --write` only when the user explicitly requests index rebuilding.
10. Report changed concept paths and any explicitly requested index results.

## Scripts

### Concept validation

```sh
python scripts/validate_frontmatter.py path/to/concept.md
```

### Explicit index rebuilding

```sh
python scripts/rebuild_indexes.py --write path/to/bundle
```

Without `--write`, index rebuilding is a dry run.

## Templates

Record owns producer templates:

- `assets/undefined_concept_template.md`
- `assets/checklist_concept_template.md`
- `assets/llm_template_concept_template.md`
- `assets/adr_concept_template.md`
- `assets/adr_register_concept_template.md`

## Safety Rules

- Require an unambiguous target bundle root; never infer one from a multi-root `MKF_PATH`.
- Do not create or update `index.md` or `log.md` as concepts.
- Do not add or maintain legacy `timestamp` or `# Citations` conventions.
- Preserve unknown frontmatter fields and existing body content.
- An explicitly requested index rebuild may replace any existing index.
- Stop and ask when `MKF_PATH` is unset, a selector is absent, or a root basename is ambiguous.
