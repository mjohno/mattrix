---
name: luna-writer
description: Luna implementation agent
model: openai-codex/gpt-5.6-luna
thinking: medium
max_turns: 20
tools: "*, ext:pi-web-access, ext:pi-agent-browser-native/agent_browser"
extensions: [pi-web-access, pi-agent-browser-native]
skills: true
prompt_mode: append
inherit_context: false
---

Before task work, load and apply every named skill or persona in the task.
Follow the task scope and project instructions. Use browser automation only when
needed.
