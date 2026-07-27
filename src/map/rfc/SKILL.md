---
name: rfc
description: Review explicitly named files through a reviewer lens, annotate prioritized findings inline, and write a connecting summary. Use when the user explicitly asks to run RFC or request-for-comment feedback.
disable-model-invocation: true
metadata:
  type: skill
  category: map
---

# rfc

Goal: Orchestrate lens-based review of target files, add concise inline annotations, and produce a summary that connects the annotations into one coherent RFC response.
Non-Goals: Remediating the findings, rewriting unrelated content, inventing criteria not supplied by the reviewer lens, or replacing a full formal `output/review` report.
Use-When: The user explicitly asks to run RFC, rfc, or request-for-comment feedback. Do not invoke automatically for generic review requests.

## 0. Prerequisites
- Explicit target file path(s) or pasted content to review; write annotations only to specifically named files
- Reviewer lens: a loaded persona skill, explicit criteria, or a named perspective from the prompt that resolves to concrete criteria
- Permission to edit the specifically named target files with inline annotations; if missing, ask before writing

## 1. Inputs
- Specifically named target files, ranges, or content from the prompt
- Reviewer lens and review criteria, resolved from persona skills when named; if a named lens cannot be resolved to concrete criteria, ask for clarification before reviewing
- Optional focus area, severity threshold using `output/review` P1-P5 semantics, output path for the summary, or annotation ID/prefix convention

## 2. Processes
1. **Scope**: Confirm the specifically named files, lens, and whether annotations should be written in-place. If the target set is ambiguous, includes only directories/globs, or write permission is absent, ask before editing.
2. **Review**: Use `output/review` semantics to produce prioritized findings from the resolved criteria and lens. Prefer findings that are specific, actionable, severity-scored, and tied to exact locations.
3. **Annotate**: Use `output/annotate` to add annotations near each accepted finding using native comment syntax. Each annotation must include a stable ID and lens in the form `REVEW(<ID>, <LENS>)`; include severity from the review finding and keep each note locally understandable.
4. **Summarize**: Write a concise RFC summary that glues the annotations together: overall judgment, themes, key risks, file-by-file note index, and suggested next action.
5. **Verify**: Re-read changed regions to ensure annotations landed near the right context, preserve formatting, and the summary references every written annotation by ID.

## 3. Outputs
- Inline `REVEW(<ID>, <LENS>)` annotations in each specifically named target file when editing is approved
- RFC summary in the prompt by default, or written to the requested output path, with every written annotation referenced by ID
- Brief verification note listing edited files and annotation count

## 4. Next Steps
- `modify` — apply accepted changes from RFC annotations
- `output/review` — produce a formal severity-scored review report
- `draft` with `interface/plan` — turn the RFC summary into a fix plan
- `step` — implement one accepted annotation at a time
- `annotate` — update, remove, or mark annotations after resolution

## 5. Examples

### Example 1

**Prompt:** "Run RFC on `docs/auth.md` using the security persona and write the summary to `docs/auth-rfc.md`."
**Outcome:** Adds security-focused `REVEW(<ID>, security)` annotations in `docs/auth.md`, writes `docs/auth-rfc.md` with themes and an annotation index, and reports edited files plus count.

### Example 2

**Prompt:** "RFC these three design docs from a system-architect lens; don't edit, just show proposed annotations and summary."
**Outcome:** Returns proposed inline `REVEW(<ID>, system-architect)` notes grouped by file and a cross-file architecture summary without modifying files.
