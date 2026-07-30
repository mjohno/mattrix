---
name: agentsmd
description: Use when output or map skills need the AGENTS.md instruction-section contract before drafting or modifying an AGENTS.md file.
metadata:
  type: interface
  category: interface
---

# agentsmd

Goal: Define the minimal AGENTS.md instruction-section contract for durable agent rules and constraints.
Non-Goals: Do not draft, modify, consolidate, move, compress, review, check, or otherwise evaluate AGENTS.md content; do not define directory inheritance or conflict precedence.
Use-When: Another skill or user prompt needs the `agentsmd` interface before drafting or modifying AGENTS.md instruction sections, including adding durable agent do's or don'ts.

## Selection

Default: load only the compact AGENTS.md instruction-section contract.

If caller intent is unclear, assume the default contract only and state the assumption.
If the caller asks to restructure, consolidate, move, compress, or assess instructions, state that this interface does not define that work and hand off to an applicable review or checklist process.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/agentsmd_contract.md`

## Next Steps

- `draft` — produce a reviewable first-pass AGENTS.md using the contract.
- `modify` — make a minimal addition to an existing AGENTS.md using the contract.
- `output/review` — assess broader AGENTS.md structure or consolidation when a review process is available.

## Minimal Example

Prompt: "Use the agentsmd interface; add these things you should do to AGENTS.md: run tests before completion."
Direct invocation response: `Loaded: references/agentsmd_contract.md.`
