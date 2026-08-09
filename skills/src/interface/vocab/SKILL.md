---
name: vocab
description: Use when a user loads definitions for terms like study, outline, modify, simplify, lean, propose, or discuss.
disable_model_invocations: true
metadata:
  type: communications
  category: interface
---

# vocab

Goal: Define compact project vocabulary for user-loaded communication context.
Non-Goals: Do not define specialized skill-owned verbs, domain glossary terms, artifact schemas, procedures, routing, or verification.

## Application

- Apply this package after the user loads it.
- Continue to apply it until the user changes or removes it.
- Apply its definitions when interpreting user requests and generating responses.
- Do not change text that must remain exact unless the user request directs that change.
- Follow higher-priority instructions when they conflict with this package.

## Controls

### Terms

- `study`: Read content to gather context. Do not modify files or execute files. Acknowledge completion of study with a minimal response. Do not summarize.
- `outline`: Produce only an artifact's structure; use concise placeholders rather than substantive content; E.g. headers, subsections, layout, function signatures, data types, or other scaffolding.
- `modify`: Make the smallest coherent requested change while preserving unrelated content and valid conventions.
- `simplify`: Reduce complexity while preserving required meaning, behavior, and useful structure.
- `lean`: Reduce overhead, waste, duplication, ceremony, or maintenance burden.
- `propose`: Write a response back to the user via chat only. Do not execute or change anything.
- `discuss`: Engage in a back-and-forth conversation with the user to clarify, explore, or refine ideas. Do not execute or change anything.
