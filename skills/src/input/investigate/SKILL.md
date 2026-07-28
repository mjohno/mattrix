---
name: investigate
description: Use when you need curious and exhaustive discovery, evidence-backed facts, and clear unknowns without remediation.
metadata:
  category: input
---

# investigate

Goal: Retrieve facts exhaustively from local files, remote systems and web sources, then turn them into a compact evidence-first YAML context summary.
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
4. **Track uncertainty**: every fact includes `confidence` and `relevance`; if a claim is not fully supported, mark it `type: tentative`, explain its relevance, and keep gathering evidence.
5. **Resolve conflicts**: present conflicting readings side by side and record what evidence would settle them.
6. **Stop when exhausted**: keep investigating until unknowns are resolved, accepted as assumptions, or the recursion limit is reached.
7. **Return YAML**: default output is YAML; do not write files unless explicitly asked.
8. **Produce Fact Summary**: include a concise and information dense summary of the main facts and unresolved unknowns.

## 3. Outputs
- YAML output in the prompt with `summary`, `facts`, and `unknowns`
- If user specifies an output file, write to that path instead

```yaml
summary: <compact evidence-backed summary>
facts:
  - fact: <fact>
    source: <file>:<line>
    confidence: <low|medium|high>
    relevance: <why this fact matters to the investigation>
  - fact: <tentative fact>
    type: tentative
    source: <file>:<line>
    confidence: <low|medium|high>
    relevance: <why this tentative fact matters and what makes it uncertain>
unknowns:
  - unknown: <follow-up investigation item or accepted assumption>
    status: <follow_up|accepted_assumption>
    next_steps: [<step>, <step>]
```

## 4. Next Steps
- `investigate` — gather more data to resolve unknowns

## 5. Examples

### Example 1
**Prompt:** Investigate `src/auth` and summarize how login works.
**Decisions:** Read local files first, cite every fact, and mark unclear behavior as tentative.
**Outcome:** YAML with `summary`, `facts` and `unknowns`, no files written.

### Example 2
**Prompt:** Investigate the README and implementation for cache invalidation.
**Decisions:** Capture both readings when they conflict, then list the evidence needed to resolve them.
**Outcome:** YAML that surfaces both interpretations and the remaining unknowns.
