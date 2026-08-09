---
name: [communications-name]
description: Use when a user loads [communication control] for LLM interpretation or generated communication.
disable_model_invocations: true
metadata:
  type: communications
  category: interface
---

<!-- Resolve every relative path in this SKILL.md from this file's directory. -->

# [communications-name]

Goal: [one clear LLM communication control]
Non-Goals: [communication behavior this package does not control]

## Application

- Apply this package after the user loads it.
- Continue to apply it until the user changes or removes it.
- Apply it only to [user-request interpretation, generated communication, or both].
- State any exclusions for code, commands, paths, identifiers, quotations, or text that must remain exact.
- Follow higher-priority instructions when they conflict with this package.

## Controls

- [one concise declarative control]
- [one concise declarative control]

[Use a package-specific subsection, such as `Terms` or `Language Rules`, when it improves clarity.]
