# MKF Record Process

## Purpose

Create or update one MKF concept safely, enforce the shared contract programmatically, and rebuild generated indexes.

## Write Flow

1. Resolve exactly one target bundle root from an explicit filesystem path or an unambiguous configured `MKF_PATH` root basename.
2. Determine the target concept path and concept ID.
3. Check for likely duplicates by:
   - exact path / concept ID
   - same frontmatter `title`
   - same frontmatter `resource`
4. Ask for confirmation before overwriting, resolving a collision, or making a substantial replacement.
5. Draft or update Markdown while preserving unknown frontmatter keys.
6. Run `scripts/validate_frontmatter.py` on changed concept files.
7. Write only valid MKF concepts.
8. Run `scripts/rebuild_indexes.py` on the affected bundle root.
9. Report changed concept and index paths.

## Scripts

### Frontmatter validation

```sh
python scripts/validate_frontmatter.py path/to/concept.md
```

Use before finalizing a concept and after generating indexes.

### Index rebuilding

```sh
python scripts/rebuild_indexes.py path/to/bundle
```

Use after successful record writes/updates.

## Templates

Record owns producer templates:

- `assets/undefined_concept_template.md`
- `assets/index_concept_template.md`
- `assets/checklist_concept_template.md`
- `assets/llm_template_concept_template.md`
- `assets/adr_concept_template.md`
- `assets/adr_register_concept_template.md`

## Safety Rules

- Require an unambiguous target bundle root; never infer one from a multi-root `MKF_PATH`.
- Do not add or maintain `timestamp`.
- Do not treat `log.md` specially.
- Do not overwrite non-generated `index.md` without explicit confirmation or a force workflow.
- Preserve source citations when updating.
- Stop and ask when `MKF_PATH` is unset, a selector is absent, or a root basename is ambiguous.
