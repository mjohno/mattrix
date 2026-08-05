---
name: review
description: Review any artifact against its criteria using one or more persona skills as evaluation perspectives.
metadata:
  type: skill
  category: output
---

# review

Goal: Compare a target artifact against pre-discovered criteria sources and persona skills, then produce a structured severity-scored report.
Non-Goals: Discover criteria or personas (that is the orchestrator's job), remediate artifacts, manage tasks, or rewrite the target.
Use-When: You need to review any artifact against its criteria using one or more evaluation perspectives.

## 0. Prerequisites

Discovery of criteria and personas is **not** the responsibility of this skill — it is assumed done by the calling agent/orchestrator (e.g. via `investigate`, `lookup`, or `remember`).

Before executing, confirm:
- **Criteria source(s)**: At least one set of evaluation criteria defining correctness for the artifact type (a canonical skill's SKILL.md, an assessment contract, a plan, quality rules, or other agreed-upon criterion). If none exist, **ask the user for them**.
- **Persona skill(s)**: At least one persona skill encoding an evaluation perspective. If none exist, **ask the user which persona to use**. The default is the base criteria below (equivalent to a generic reviewer).

You may accept both from the same prompt or request them separately if missing.

## 1. Inputs
| Input | Required | Example |
|---|---|---|
| Target artifact | Yes | `SPEC-001.md` or pasted content |
| Criteria source(s) | Yes | RFC skill's SKILL.md, assessment contract, plan, quality rules, or file path |
| Persona skill(s) | No | `security`, `adversarial`, `system_architect` (discovered and resolved by orchestrator) |
| Diff refs | No | "main to HEAD" for diff review |

## 2. Processes

### Evaluation criteria (always applied)
- **Internal Consistency**: No contradictions within the artifact; terminology used consistently.
- **Clarity**: Language is precise and unambiguous; reader understands intent without guessing.

### Step-by-step Workflow
1. **Load criteria** from pre-discovered sources
2. **Apply base criteria** (internal consistency, clarity)
3. **For each persona skill**, apply its evaluation criteria on top of loaded criteria + base
4. **Compare target** against combined criteria — note where it matches, deviates, or omits
5. **Categorize findings** by severity (P1–P5 per `assets/severity.md`)
6. **Report via template** (`assets/template_report.md`) with findings and recommended changes

## 3. Outputs
Structured review report using `assets/template_report.md` with findings categorized P1–P5 per `assets/severity.md`. Default: output to prompt. Write to file when an output path is provided.

## 4. Next Steps
- `output/check` — run a check on the artifact against requirements, checklists, acceptance or target criteria
- `output/review` — re-review after fixes are applied
- `output/annotate` — add inline annotations for tracking findings (NOTE) and fixes (TODO)
- `draft` with `interface/plan` — create a plan to address findings

### Constraints
1. Cite exact criteria sources for every finding
2. Every finding suggests a concrete change
3. Never introduce requirements beyond the loaded criteria
4. Findings are numbered sequentially within each severity heading; restart at 1 in each section (P1, P2, etc.)
5. Report both missing AND incorrect elements
6. No remediation — only comparison and reporting

## 5. Examples

### Example 1: Single persona review
**Prompt:** "Review RFC-001.md using the `security` persona."  
→ Orchestrator has resolved criteria (RFC skill's SKILL.md) and persona (`security`) → review runs base criteria + security evaluation → P1-P5 report.

### Example 2: Multi-persona review
**Prompt:** "Review this diff from main to HEAD with both `adversarial` and `system_architect` perspectives."  
→ Orchestrator provides persona skills, target is the diff content → review runs base criteria + adversarial + system_architect evaluation → scoped P1-P5 report.

### Example 3: Missing prerequisites
**Prompt:** "Review SPEC-012.md."
→ No criteria provided, no persona provided → SKILL.md asks user to supply them before proceeding.

### Example 4: Report structure
**Prompt:** "Review the assessment contract against RFC-005 with `security` lens."
→ Orchestrator provides criteria (RFC-005) + persona (`security`) → review produces:
   - Findings numbered 1–3 under P1, restart at 1 for P2, restart at 1 for P3
   - Sections skip severity tiers with zero findings (e.g., no P4/P5 heading if none exist)
   - Recommended Changes listed separately after all findings
