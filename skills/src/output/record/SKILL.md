---
name: record
description: Use when durable MKF knowledge content needs to be created or updated.
metadata:
  type: skill
  category: output
  capabilities:
    - knowledge
    - mkf
    - okf
---
# record

Goal: Safely create or update one MKF concept.
Non-Goals: Do not opportunistically record, perform broad lookup, synthesize final advice, write reserved files as concepts, or rebuild indexes unless explicitly requested.
Use-When: The user explicitly asks to record durable knowledge or a workflow explicitly triggers MKF recording.

## 0. Prerequisites
- One unambiguous `MKF_PATH` root basename or explicit bundle path
- Shared contract: `../../interface/knowledge-base/SKILL.md`
- MKF contract: `../../interface/knowledge-base/references/mkf_contract.md`
- Record process: `references/record_process.md`

## 1. Inputs
- MKF concept content or raw source material
- Target bundle and optional folder/concept path
- Optional explicit advanced-OKF metadata request
- Optional explicit index-rebuild request

## 2. Processes
1. Read the shared knowledge-base references only as needed.
2. Resolve exactly one target bundle root from an explicit path or an unambiguous `MKF_PATH` basename; ask when missing or ambiguous.
3. Reject `index.md` and `log.md` as concept targets; check concept collisions and ask before overwrite or substantial replacement.
4. Draft or update the concept, preserving unknown frontmatter keys and existing body content.
5. Run `scripts/validate_frontmatter.py` before finalizing written concepts.
6. Rebuild indexes with `scripts/rebuild_indexes.py` only when the user explicitly requests it; report changed paths.

## 3. Outputs
- Created or updated concept path
- Validation result
- Explicit index-rebuild result, when requested
- Concise write summary

## 4. Next Steps
- `../../input/lookup/SKILL.md` — retrieve existing concepts before writing or to verify discoverability
- `../../interface/knowledge-base/references/mkf_contract.md` — interpret baseline concept requirements

## 5. Examples

### Example 1

**Prompt:** Record this as a checklist in the uniquely named `general` root on `MKF_PATH`.
**Outcome:** Resolves one root, writes one valid concept, validates it, and reports the changed concept path.

### Example 2

**Prompt:** Rebuild indexes for this bundle after recording the concept.
**Outcome:** After the concept write, explicitly runs index rebuilding and reports changed and skipped index paths.
