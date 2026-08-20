---
name: investigate
description: Use when you need curious and exhaustive discovery, evidence-backed facts, and clear unknowns without remediation.
metadata:
  category: input
---

# investigate

Goal: Retrieve facts exhaustively from local files, remote systems and web sources, then turn them into a compact evidence-first Markdown investigation with referencable findings.
Non-Goals: Remediation, implementation plans, or speculative conclusions.
Use-When: You need to investigate a codebase, docs, databases, SaaS or other sources to build accurate context.

## 0. Prerequisites
- Target scope: files, directories, or topics to investigate

## 1. Inputs
- Target scope from prompt (file paths, directories, or topics)
- Recursion or time limits (optional)

## 2. Processes
1. **Scope first**: confirm the objective, scope, and any recursion limit (default: unlimited) or time limit.
2. **Collect evidence**: prefer local files first; use web sources, CLI's, API's for SaaS and other systems only when asked or when local evidence is insufficient.
3. **Deduplicate evidence**: remove repeated sources, repeated claims, and overlapping facts while preserving the strongest citation for each fact.
4. **Track uncertainty**: every finding includes confidence and relevance; if a claim is not fully supported, mark it as tentative, explain its relevance, and keep gathering evidence.
5. **Resolve conflicts**: present conflicting readings side by side, link the relevant findings, and record what evidence would settle them.
6. **Stop when exhausted**: keep investigating until unknowns are resolved, accepted as assumptions, or the recursion limit is reached.
7. **Return Markdown**: default output is Markdown; do not write files unless explicitly asked.
8. **Produce Fact Summary**: include a concise and information-dense summary of the main facts and unresolved unknowns.

## 3. Outputs
- Markdown output in the prompt with a summary, numbered findings, conflicts, and unknowns
- Each finding has a unique `F-###` identifier that readers can reference
- If user specifies an output file, write to that path instead

```markdown
# Investigation: <title>

## Summary

<compact evidence-backed summary>

## Findings

### F-001: <finding title>

- **Claim:** <fact or tentative fact>
- **Type:** <fact|tentative>
- **Evidence:** `<file>:<line>`
- **Confidence:** <low|medium|high>
- **Relevance:** <why this matters>

## Conflicts

### C-001: <conflict title>

- **Finding A:** [F-001](#f-001-finding-title)
- **Finding B:** [F-002](#f-002-finding-title)
- **Evidence needed:** <evidence that resolves the conflict>

## Unknowns

### U-001: <unknown title>

- **Status:** <follow_up|accepted_assumption>
- **Related findings:** [F-001](#f-001-finding-title)
- **Next steps:** <steps>
```

## 4. Next Steps
- `investigate` — gather more data to resolve unknowns

## 5. Examples

### Example 1
**Prompt:** Investigate `src/auth` and summarize how login works.
**Decisions:** Read local files first, cite every fact, and mark unclear behavior as tentative.
**Outcome:** Markdown with a summary, referencable findings, and unknowns; no files written.

### Example 2
**Prompt:** Investigate the README and implementation for cache invalidation.
**Decisions:** Capture both readings when they conflict, then list the evidence needed to resolve them.
**Outcome:** Markdown that links the conflicting findings and lists the remaining unknowns.
