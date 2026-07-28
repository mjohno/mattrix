---
name: vocab
description: Use when terms like study, outline, draft, modify, simplify, lean, propose need definition.
disable_model_invocations: true
metadata:
  type: vocabulary
  category: interface
---

# vocab

Goal: Define compact project vocabulary for human-loaded context before prompting.
Non-Goals: Do not define specialized skill-owned verbs, domain glossary terms, inputs, outputs, procedures, routing, or verification.

## Terms

- `study`: Read content to gather context. Do not modify files or execute files. Acknowledge completion of study with a minimal response. Do not summarize.
- `outline`: Produce only an artifact's structure; use concise placeholders rather than substantive content; E.g. headers, subsections, layout, function signatures, data types, or other scaffolding.
- `draft`: Produce a reviewable first pass; preserve uncertainties as explicit placeholders.
- `modify`: Make the smallest coherent requested change while preserving unrelated content and valid conventions.
- `simplify`: Reduce complexity while preserving required meaning, behavior, and useful structure.
- `lean`: Reduce overhead, waste, duplication, ceremony, or maintenance burden.
- `propose`: Write a response back to the user via chat only. Do not execute or change anything.
- `discuss`: Engage in a back-and-forth conversation with the user to clarify, explore, or refine ideas. Do not execute or change anything.

