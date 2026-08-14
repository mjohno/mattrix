---
name: lookup
description: Use when the user explicitly asks for an MKF or OKF knowledge lookup.
metadata:
  type: skill
  category: input
  capabilities:
    - knowledge
    - mkf
    - okf
---
# lookup

Goal: Retrieve best MKF metadata matches so selected concept files can be loaded as context.
Non-Goals: Do not write concepts, rebuild indexes, validate writes, or synthesize final advice from matches.
Use-When: The user explicitly asks to look up durable knowledge or retrieve MKF or OKF context.

## 0. Prerequisites
- User query text
- Bundle selector(s), all-bundle request, or explicit bundle path
- Shared contract: `../../interface/knowledge-base/SKILL.md`
- MKF contract: `../../interface/knowledge-base/references/mkf_contract.md`
- Bundle discovery: `references/bundle_discovery.md`
- Lookup process: `references/lookup_process.md`

## 1. Inputs
- Query text
- Optional unambiguous configured bundle-root basenames or filesystem bundle paths
- Optional explicit advanced-OKF field filters
- Optional result limit

## 2. Processes
1. Read the shared knowledge-base references only as needed.
2. Resolve selected bundle roots using lookup-owned `references/bundle_discovery.md`.
3. Use `scripts/search_mkf.py` instead of ad hoc grep.
4. Search valid concepts in deterministic order: resolved bundle path order, directory/file/concept-name matches, core frontmatter metadata, then body content.
5. Exclude reserved `index.md` and `log.md` files from concept results; treat indexes as progressive-disclosure material, not search authority.
6. Return partial matches with structured errors for unreadable or invalid concept candidates.
7. Load full concept files only after the user or workflow selects matches that need full context.

## 3. Outputs
- Metadata match records with bundle, path, concept ID, type, title, description, tags, match tier, score, and excerpt when useful
- Structured errors for invalid or unreadable candidates
- Empty result only when no useful matches exist

## 4. Next Steps
- `../../output/record/SKILL.md` — create or update durable concepts
- `../../interface/knowledge-base/references/mkf_contract.md` — interpret selected concept structure

## 5. Examples

### Example 1

**Prompt:** Look up checklist concepts in the `general` root on `MKF_PATH`.
**Outcome:** Runs `scripts/search_mkf.py`, returns matching concept metadata, and does not synthesize advice.
