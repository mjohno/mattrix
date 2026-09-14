---
name: slides
description: Use when work needs a concise Markdown slide deck.
metadata:
  type: interface
  category: interface
---

# slides

Goal: Define a concise Markdown slide-deck contract.
Non-Goals: Do not research, write, render, present, review, or publish a deck.
Use-When: Another skill needs slide-deck structure before it outlines, drafts, modifies, checks, or reviews a deck.

## Selection

Default: load only `references/slides_contract.md`.

Also select:
- `assets/slides_template.md` when the caller asks for a starting deck structure.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

## Minimal Example

Prompt: "Use the `slides` interface to draft a project update."
Direct invocation response: `Loaded: references/slides_contract.md.`
