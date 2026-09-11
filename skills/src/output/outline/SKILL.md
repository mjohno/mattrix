---
name: outline
description: Use when you need the structure of a desired artifact or artifact type without producing the finished artifact.
metadata:
  type: skill
  category: output
---

# Outline

Goal: Produce a structural representation of a requested artifact or artifact type.
Non-Goals: Do not produce the finished artifact, implementation code, or files unless explicitly requested.
Use-When: Use when a user asks to outline a project, code change, test, document, slide deck, diagram, or other artifact.

## 0. Prerequisites

- Identify the artifact type, requested scope, and known constraints.
- Read relevant existing content when the outline concerns a change or refactor.

## 1. Inputs

- The requested artifact type, goal, scope, and known constraints.
- Relevant existing content when the outline concerns a change or refactor.

## 2. Processes

1. Select the format that best shows the requested structure.
2. Describe organisation, responsibilities, boundaries, and relationships.
3. Use concise placeholders where content is not yet known.
4. Add an ASCII or Mermaid diagram only when it improves review.
5. Do not add finished content or implementation unless requested.

### Context Formats

- **Files or projects:** directory and file tree; major component relationships where useful.
- **Source code:** types, interfaces, data structures, signatures, inputs, outputs, and responsibilities.
- **Fixes or refactors:** affected locations, changed logic, dependencies, and current versus proposed flow.
- **Tests:** behaviour, unit boundary, seams, collaborators, inputs, outputs, and isolation method.
- **Documents:** headings, section purpose, and idea flow.
- **Slide decks:** slide title, optional subtitle, key message, and narrative progression.
- **Diagrams:** conceptual entities and relationships; prefer Mermaid, then ASCII.

## 3. Outputs

- Return the outline in chat by default.
- Do not write files unless the user explicitly requests a destination.
- Make the result structural rather than complete.

## 4. Next Steps

- `draft` — turn the outline into a first-pass artifact.
- `modify` — apply an approved outline to an existing artifact.
- `spec` — load a future-state specification contract when needed.

## 5. Examples

### Example 1 — Document

**Prompt:** "Outline a proposal for a payment retry service."
**Outcome:** Document headings, section purposes, and the intended flow from problem through decision; no proposal text.

### Example 2 — Source Code

**Prompt:** "Outline the payment retry service implementation."
**Outcome:** Service types, public methods, inputs, return values, dependencies, and responsibilities; no implementation code.

### Example 3 — File System

**Prompt:** "Outline the files for the payment retry service."
**Outcome:** A directory tree with proposed file names and their major relationships; no files created.
