---
name: handoff
description: Use when an agent must prepare compact work state for a fresh session.
metadata:
  type: skill
  category: output
---

# handoff

Goal: Produce a compact handoff for a fresh agent session.
Non-Goals: Do not store a transcript, duplicate existing artifacts, create a change path, or store secrets.
Use-When: Use when work will continue in a new session or by another agent.

## 0. Prerequisites
- Current conversation context.
- `interface/change` when the caller supplies a change path.

## 1. Inputs
- Optional next-session focus.
- Optional caller-provided change path.
- Current goal, state, decisions, next actions, and artifact references.

## 2. Processes
1. Use the supplied focus as `Next-Session Focus`. Otherwise, use the current goal.
2. Infer a new short kebab-case slug from the focus or goal. If `HANDOFF-<slug>.md` exists, append `-1` to the slug.
3. Build a document titled `# Handoff: <Title>` with `HANDOFF_ID: HANDOFF-<slug>`, `Source`, and `Purpose` metadata. Add `Next-Session Focus`, `Goal`, `Current State`, `Completed`, `Next`, `Decisions`, `Open Questions`, `References`, and `Suggested Skills` sections.
4. Capture only information needed to continue work. Reference existing artifacts by path, URL, or stable ID. Do not copy them. Remove secrets and personal data.
5. If a change path exists, write `HANDOFF-<slug>.md` there. Otherwise, return the document in chat only.

## 3. Outputs
- A handoff document with the required sections.
- `<change-path>/HANDOFF-<slug>.md` when a change path is supplied.
- Copy-ready handoff Markdown when no change path is supplied.

## 4. Next Steps
- Start a fresh session with the handoff document.
- Continue from `## Next`.
- Load skills in `## Suggested Skills` when applicable.

## 5. Examples

### Example 1

**Prompt:** `handoff: Draft the replacement skill package.`
**Outcome:** Returns a copy-ready handoff when no change path is supplied.
