---
name: review
description: Review an artifact against applicable criteria and produce a structured severity-scored report. Use when you need a traceable review report.
metadata:
  type: skill
  category: output
---

# review

Goal: Compare a target artifact against applicable criteria and produce a structured severity-scored report.
Non-Goals: Do not do broad external criteria research, remediate the target, manage tasks, or rewrite the target.
Use-When: You need to review an artifact against its criteria.

## 0. Prerequisites
- A target artifact.
- An applicable criteria source, resolved from user-provided sources or local contracts. Ask the user only when no applicable source can be determined.

## 1. Inputs
- Target artifact, such as a file path or pasted content.
- Criteria sources named by the user, when provided.
- Diff references, when the target is a diff.

## 2. Processes
1. Resolve criteria sources: use user-named sources; identify the target type; select the smallest applicable local specification, contract, checklist, rubric, plan, quality rule, or acceptance criteria; and ask the user only when no applicable source can be determined or the target type is ambiguous enough to change the review result.
2. Apply the base criteria:
   - **Internal Consistency**: The artifact has no contradictions and uses terms consistently.
   - **Clarity**: The language is precise and the reader can understand the intent without guessing.
3. Compare the target against the combined criteria. Identify matches, deviations, and omissions.
4. Categorize findings by severity (P1–P5 per `assets/severity.md`).
5. Produce a report using `assets/template_report.md`.

Include an applicable specification as criteria when one exists, whether or not the user named it. Do not create requirements that are not present in the selected criteria sources.

## 3. Outputs
- A structured review report using `assets/template_report.md`.
- The target artifact and review scope.
- The selected criteria sources.
- Findings grouped by severity, with a concrete recommended change for each finding.
- Review limits or unresolved scope uncertainty, when material.

Output to chat by default. Write the report to a file when the user provides an output path.

## 4. Next Steps
- `output/check` — Validate the artifact against requirements or acceptance criteria.
- `output/review` — Re-review the artifact after changes.
- `output/annotate` — Add inline annotations for findings and fixes.
- `draft` with `interface/plan` — Draft a plan to address findings.

## 5. Constraints
1. Cite an exact selected criteria source for every finding.
2. Give a concrete recommended change for every finding.
3. Do not introduce requirements beyond the selected criteria.
4. Identify findings as `P1.1`, `P1.2`, and so on. Restart the number at `1` for each severity.
5. Report missing and incorrect elements.
6. Do not remediate the target. Only compare and report.

## 6. Examples

### Example 1: Review with named criteria

**Prompt:** Review `RUBRIC-001.md` against `interface/rubric`.

**Outcome:** Load the rubric contract, apply the base criteria, and produce a P1–P5 review report.

### Example 2: Review with an unlisted specification

**Prompt:** Review `SPEC-012.md`.

**Outcome:** Identify `SPEC-012.md` as a specification, load the applicable local specification contract, apply the base criteria, and produce a review report.

### Example 3: Missing criteria

**Prompt:** Review this document.

**Outcome:** Identify the document type when possible. If no applicable local criteria source can be determined, ask the user to provide criteria or clarify the target type.
