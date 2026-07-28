---
name: script
description: Use when output or map skills need script-domain conventions, quality checks, and templates.
metadata:
  type: interface
  category: interface
---

# script

Goal: Define the minimal script artifact contract and optional domain-specific conventions, checks, and templates.
Non-Goals: Do not write, modify, execute, test, deploy, or persist scripts.
Use-When: Another skill needs the `script` interface before drafting, modifying, checking, reviewing, or orchestrating a script artifact.

## Selection

Default: load only the compact script contract.

Also select:
- `python_contract.md` when Python is selected from language, file extension, shebang, runtime clues, or unspecified language default.
- `python_template.py` when the caller asks to outline or draft a Python script.
- `script_checklist.md` when the caller asks to check script conformance.
- `script_quality.md` when the caller asks to review script quality.

If caller intent is unclear, assume default contract only and state the assumption.
If the script domain is unsupported, return the generic contract, state unavailable domain-specific refs/assets, and hand off to `modify` to add a domain reference.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/script_contract.md`

Optional paths:
- `references/python_contract.md`
- `assets/python_template.py`
- `references/script_checklist.md`
- `references/script_quality.md`

## Next Steps

- `outline` — create a script skeleton using applicable template data.
- `draft` — produce a first-pass script.
- `modify` — update an existing script against the contract.
- `output/check` — check script conformance with `script_checklist.md`.
- `output/review` — review script quality with `script_quality.md`.
- `map/step` — run a bounded implementation or verification step.

## Minimal Example

Prompt: "Use the script interface for a file organizer script with dry-run support."
Direct invocation response: `Loaded: references/script_contract.md.`
