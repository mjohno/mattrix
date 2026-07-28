# Memory Contract

Memory is a shared Markdown file containing durable summary material and an append-only log.

## File Selection

Resolve memory files in this order:
1. Prompt-provided memory file path.
2. `MEMORY_FILE` environment variable.
3. `.memory.md` in the current working directory.

Do not introduce `MEMORY_ROOT`, named memory locations, or project/global config files.

## Required Shape

```text
# Summary

- <durable fact, decision, preference, or project context>

# Memory Log

## <UTC ISO-8601 timestamp with Z>

- <clear memory entry>
```

## Entry Shape

```yaml
content:
id:
date:
kind: preference | fact | decision | reminder | thread | temporary | project-context
source:
confidence:
expires:
tags:
promote_to_kb:
```

Only `content` is required. Keep entries lightweight and render them as clear bullets, not raw transcripts.

## Rules

- `# Summary` is the durable memory record.
- Destructive summary rewrites require user approval.
- Use UTC ISO-8601 timestamps with `Z` for log headings.
- Append under an existing same-second heading when present.
- If the file is missing and a write is explicitly requested, initialize the standard skeleton.
- Mark contradictions or replacement candidates when approval is required.
- Routine compression may happen later; destructive rewrites still require approval.

## Minimal Example

```text
# Summary

- User prefers concise status reports.

# Memory Log

## 2026-01-01T00:00:00Z

- preference: User prefers concise status reports. Source: conversation.
```
