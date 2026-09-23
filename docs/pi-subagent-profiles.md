---
type: configuration
title: Pi Subagent Profiles
---

# Pi Subagent Profiles

## Purpose

Define four global Pi subagent profiles. The profiles vary only by model and
local-write permission.

The authoritative implementations are in `agents/pi-subagents/`:

- `luna-reader.md`
- `luna-writer.md`
- `sol-reader.md`
- `sol-writer.md`

`~/.pi/agent/agents` is a symbolic link to `agents/pi-subagents/`, which makes
these profiles available to Pi globally.

## Design Decisions

### Model profiles

- Luna profiles use `openai-codex/gpt-6-luna`.
- Sol profiles use `openai-codex/gpt-6-sol`.

### Permission profiles

- A reader can use `read`, `grep`, `find`, `ls`, and `pi-web-access`.
  It cannot use `bash`, edit local files, or write local files.
- A writer has all built-in tools. It can also use `pi-web-access` and
  `agent_browser` from `pi-agent-browser-native`.

### Shared execution policy

All profiles use:

- `thinking: medium`
- `max_turns: 20`
- `skills: true`
- `prompt_mode: append`
- `inherit_context: false`

The profile instruction requires the agent to load and apply every skill or
persona named in its task before task work begins.

## Implementation

| Profile | Model | Local tools | Extensions |
| --- | --- | --- | --- |
| `luna-reader` | `openai-codex/gpt-6-luna` | Read-only tools | `pi-web-access` |
| `luna-writer` | `openai-codex/gpt-6-luna` | All built-in tools | `pi-web-access`, `pi-agent-browser-native` |
| `sol-reader` | `openai-codex/gpt-6-sol` | Read-only tools | `pi-web-access` |
| `sol-writer` | `openai-codex/gpt-6-sol` | All built-in tools | `pi-web-access`, `pi-agent-browser-native` |

## Usage

Name the profile and the required skills or personas in the delegated task.
For example:

> Use `luna-reader`. Load `review` and `adversarial`, then review the current diff.

## Indexing

No index rebuild was requested.
