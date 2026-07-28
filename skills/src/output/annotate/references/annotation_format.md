# Annotation Format

Annotations are structured, actionable notes embedded in files. They are inline task carriers with embedded status — not passive comments.

## Format

```text
<KIND>(<ID>): <message>
refs: [<source reference>, ...]
```

- `<KIND>` — one of the peer tags below (NOTE, TODO, CHECK, REVIEW, DONE)
- `<ID>` — stable traceable anchor; keep it consistent when the note's purpose changes
- `<message>` — concise description of the annotation's intent
- `refs:` — optional list of source references; composable, uncoupled from any domain

## Kinds (peer tags, no hierarchy)

| Kind | Purpose | Status |
|---|---|---|
| `NOTE` | Knowledge, information, context | Informational — no action required |
| `TODO` | Action item (inline task carrier) | Pending — someone should do this |
| `CHECK` | Testing/verification to perform | Pending — someone should verify this |
| `REVIEW` | Comparison against a source reference | Pending — someone should review this |
| `DONE` | Completion mark | Complete — marks work as finished |

Status is encoded in the kind itself:
- `NOTE` and `DONE` are terminal states (informational and complete)
- `TODO`, `CHECK`, and `REVIEW` are pending states (action required)
- When a pending annotation is complete, change its kind to `DONE` and preserve the ID

## Source references

`refs:` supports composable, domain-agnostic references:

```text
refs: [auth/middleware.ts:42]          # file:line
refs: [SPEC-AUTH.md#ACC-3]              # file#anchor
refs: [https://example.com/spec#D-2]  # url#anchor
refs: [SPEC-AUTH.md#ACC-3, RFC-AUTH#D-2]  # multiple refs
```

Rules:
- Use `file:line` for precise code locations
- Use `file#anchor` for document sections (headings, acceptance criteria, etc.)
- Use `url#anchor` for external references
- Multiple refs are allowed; keep them concise
- Do not couple refs to specific domains (spec, RFC, etc.) — use whatever naming convention the source material uses

