---
name: draft
description: Use when current context, ideas, and known information need a structured first-pass artifact without filling gaps by assumption.
metadata:
  type: skill
  category: output
---

# draft

Goal: Turn available context into a structured, reviewable first-pass artifact with its known information and material uncertainty faithfully represented.
Non-Goals: Do not investigate missing facts, invent details, resolve decisions, verify claims, or implement the drafted work.
Use-When: Existing context, notes, ideas, or source material need to be captured in a draft, especially when an interface such as `slides`, `spec`, or `plan` supplies the artifact structure.

## 0. Prerequisites

- Supplied context, source material, or an existing artifact to capture.
- An applicable interface contract, template, or requested structure when the artifact type has one.

## 1. Inputs

- Available facts, ideas, source references, constraints, and existing artifact content.
- Requested audience, purpose, destination, and format, when known.
- A selected interface's contract or template, when supplied or applicable.

## 2. Processes

1. Identify the requested artifact and apply its supplied structural framework; when none is supplied, use a minimal structure appropriate to the request.
2. Extract and organize only information present in the inputs; preserve source attribution or qualification when available.
3. Populate each supported section with available content without extending facts, implications, commitments, or decisions beyond the evidence.
4. Label every material ambiguity, assumption, risk, missing input, unresolved decision, and incomplete section explicitly.
5. Distinguish confirmed content from ideas, proposals, and unknowns; leave unsupported sections marked rather than completing them by guesswork.

## 3. Outputs

- One structured, reviewable draft in the requested format or destination.
- An explicit `Open Questions`, `Assumptions`, `Risks`, and `Decisions Needed` section when those categories are material; use `None identified from supplied context` only when supported.
- If a structural framework cannot be determined, a minimal draft plus a clearly labeled format uncertainty.

## 4. Next Steps

- `investigate` — gather evidence for open questions or missing facts.
- `grill-me` — elicit or challenge unresolved assumptions and decisions.
- `modify` — revise an approved draft with newly supplied information.
- `check` — validate the completed artifact against its contract or acceptance criteria.

## 5. Examples

### Example 1

**Prompt:** Use the `slides` interface to `draft` a project kickoff deck from these meeting notes.
**Outcome:** Return a deck-shaped first pass that uses only the notes, marks unsupported slides as incomplete, and lists open questions, assumptions, risks, and decisions needed.
