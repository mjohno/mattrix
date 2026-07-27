---
name: memory
description: Use when remember, memorize, learn, or dream needs the shared memory file and content contract.
metadata:
  type: interface
  category: interface
  capabilities:
    - memory
---
# memory

Goal: Define the shared memory artifact contract for file selection, sections, entry shape, summary shape, and safety rules.
Non-Goals: Do not retrieve, write, synthesize, clean, compress, or persist memory directly.
Use-When: Another skill needs the `memory` interface contract before remembering, memorizing, learning from, or cleaning memory.

## Selection

Default: load only the compact memory contract.

If caller intent is unclear, assume default contract only and state the assumption.
If requested memory needs fall outside this interface, state the unsupported need and hand off to the appropriate skill.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/memory_contract.md`

## Next Steps

- `input/remember` — retrieve structured memory context.
- `output/memorize` — append memory log entries.
- `map/dream` — compact and rewrite memory summary/log with approval where required.

## Minimal Example

Prompt: "Use the memory interface to define shared memory rules."
Direct invocation response: `Loaded: references/memory_contract.md.`
