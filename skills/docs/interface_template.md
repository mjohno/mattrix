---
name: [interface-name]
description: ["Use when..." triggers for loading this interface]
metadata:
  type: interface
  category: interface
---

<!-- For context-only project terms, use vocab_template.md instead. -->
<!-- Resolve every relative path in this SKILL.md from this file's directory. -->

# [interface-name]

Goal: [one clear noun/domain contract this interface exposes]
Non-Goals: [work this interface does not perform]
Use-When: [triggers for loading this interface as passive contract context]

## Selection

Default: load only the minimal contract reference needed for common use.

Also select:
- `[optional_reference].md` when [explicit caller intent/domain condition].
- `[optional_asset]` when [explicit caller intent/domain condition].

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/[minimal_contract].md`

Optional paths:
- `references/[optional_reference].md`
- `assets/[optional_asset]`

## Next Steps

- [downstream skill] — [how it consumes this interface]

## Minimal Example

Prompt: "Use the `[interface-name]` interface for `[artifact/context]`."
Direct invocation response: `Loaded: references/[minimal_contract].md.`
