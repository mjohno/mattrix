---
name: record
description: Use when durable MKF knowledge content needs to be created or updated.
metadata:
  type: skill
  category: output
  capabilities:
    - knowledge
    - mkf
---
# record

Goal: Safely create or update one MKF concept and rebuild generated indexes.
Non-Goals: Do not opportunistically record, perform broad lookup, or synthesize final advice.
Use-When: The user explicitly asks to record durable knowledge or a workflow explicitly triggers MKF recording.

## 0. Prerequisites
- One unambiguous `MKF_PATH` root basename or explicit bundle path
- Shared contract: `../../interface/knowledge-base/SKILL.md`
- Knowledge contract: `../../interface/knowledge-base/references/knowledge_contract.md`
- Record process: `references/record_process.md`

## 1. Inputs
- MKF concept content or raw source material
- Target bundle and optional folder/concept path
- Optional provenance/source references
- Optional concept type: `undefined`, `index`, `checklist`, `template`, `adr`, `adr-index`, or another type

## 2. Processes
1. Read the shared `knowledge-base` references only as needed.
2. Resolve exactly one target bundle root from an explicit path or an unambiguous `MKF_PATH` basename; ask when missing or ambiguous.
3. Determine concept path/ID, check collisions by path/title/resource, and ask before overwrite or substantial replacement.
4. Draft or update the concept using local templates when useful, preserving unknown frontmatter keys and citations.
5. Run `scripts/validate_frontmatter.py` before finalizing written concepts.
6. After successful writes/updates, run `scripts/rebuild_indexes.py` for the affected bundle and report changed paths.

## 3. Outputs
- Created or updated MKF concept path
- Validation result
- Index rebuild result
- Concise write summary

## 4. Next Steps
- `../../input/lookup/SKILL.md` — retrieve existing MKF concepts before writing or to verify discoverability
- `../../interface/knowledge-base/references/knowledge_contract.md` — interpret concept requirements

## 5. Examples

### Example 1

**Prompt:** Record this as a checklist in the uniquely named `general` root on `MKF_PATH`.
**Outcome:** Resolves one bundle root, writes one MKF concept with valid frontmatter, validates it, rebuilds generated indexes for the bundle, and reports the changed files.
