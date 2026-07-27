---
name: check
description: Use when you need to validate whether an object, solution, result or outcome meets its target or acceptance criteria.
metadata:
  type: skill
  category: output
---

# check

Goal: Determine pass/partial/fail status of an object, result, outcome, or factual claim against defined target criteria, acceptance criteria, requirements, or source evidence.
Non-Goals: Fixing failures, implementing solutions, making final go/no-go decisions, or performing broad discovery of missing sources.
Use-When: Use when you need to validate whether an object, solution, result, outcome, or claim meets its target or acceptance criteria.

## 0. Prerequisites
- Prompt, context or files with the object, solution, result or outcome to evaluate (e.g. prototype, PoC, test results)
- Prompt, context or files with the requirements, acceptance criteria, target outcomes, or source evidence to evaluate against (e.g. Specifications, Plans, Documentation, Hypotheses, cited sources)

## 1. Inputs
- Object, solution, result or outcome to evaluate (e.g. prototype, PoC, test results)
- Requirements, acceptance criteria, target outcomes, or source evidence to evaluate against (e.g. project documentation, plan done criteria, cited files, URLs, tool output, or user-provided sources)

## 2. Processes
1. Extract requirements, acceptance criteria or target outcomes from provided context or files
2. Extract relevant information about the object, solution, result or outcome to evaluate from provided context
3. Check if delivery was successful
4. Check if delivery is complete
5. When checking factual claims or sourced outputs, compare each claim against the provided sources and classify provenance as `supported`, `unsupported`, `contradicted`, or `insufficient evidence`.
6. Cite source references for provenance-sensitive checks when sources are provided or required by the criteria.
7. Capture any partial successes or failures, and document confidence (high, medium, low) and impact (high, medium, low) for each requirement
8. Capture if there are blockers or dependencies which indicate an error in the requirements, acceptance criteria or target outcomes themselves

## 3. Outputs
- Pass/Partial/Fail status for each requirement, acceptance criteria or target outcome
- Provenance status (`supported`, `unsupported`, `contradicted`, or `insufficient evidence`) for claim/source checks
- Severity and impact documentation for any partial successes or failures
- List the blockers or dependencies identified, and whether they indicate an error in the requirements, acceptance criteria or target outcomes themselves
- If user specifies an output file, write to that path instead

## 4. Next Steps
- Suggest how to address any failures or partial success to meet the requirements, acceptance criteria or target outcomes
- Offer to create or update a plan or task list to address any failures or partial successes
- When there are blockers or dependencies, suggest how to address those.

## 5. Examples

### Example 1: Requirements check

**Prompt:** Check the prototype against the requirements outlined in the project documentation.
**Outcome:** Prompt output with requirement-by-requirement evaluation: 9 passed, 2 partial, 1 fail, with severity and impact documented for each.

### Example 2: Hypothesis check

**Prompt:** Check whether the hypothesis is valid given the results of the report.
**Outcome:** Prompt output with hypothesis evaluation: supported/not supported/insufficient evidence, provenance status where source evidence is provided, plus high/medium/low confidence level and data needed for further checks.

### Example 3: Task completion check

**Prompt:** Check whether the completed tasks meet the acceptance criteria outlined in the project plan.
**Outcome:** Prompt output with task evaluation: 5 tasks passed, 3 tasks partially met. Provided suggestions for how to address the partial successes.
