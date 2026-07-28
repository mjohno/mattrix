---
name: remember
description: Use when the user explicitly asks to retrieve memory from a selected memory file.
metadata:
  type: skill
  category: input
  capabilities:
    - memory
---
# remember

Goal: Retrieve structured memory context without synthesizing a final answer.
Non-Goals: Writing memory, deduplicating memory, or deciding summary rewrites.
Use-When: The user explicitly asks to remember, inspect, or retrieve prior memory.

## 0. Prerequisites
- A resolved memory file
- The `interface/memory` contract

## 1. Inputs
- User query text
- Optional memory file path or `MEMORY_FILE`
- Optional topic, project, date, kind, or thread selectors

## 2. Processes
1. Read and follow the `interface/memory` contract.
2. Resolve the memory file from prompt path first, then `MEMORY_FILE`, then `.memory.md` in the current working directory.
3. If the resolved memory file does not exist, report that it does not exist.
4. Search `# Summary` first, then `# Memory Log`.
5. Return Summary matches plus only non-duplicative or new Memory Log matches.
6. Use exact/lexical retrieval first; if nothing matches, try light query expansion such as singular/plural, hyphen/space variants, and obvious query-context synonyms.
7. Do not apply a default result limit; the memory file is a single file, not a recursive tree.
8. Return structured raw memory context only.
9. When no useful memory exists, return an empty result only.

## 3. Outputs
- Memory matches with section, timestamp if applicable, and relevant excerpt or structured fields
- Empty result only when nothing useful is found

## 4. Next Steps
- `interface/memory` — shape retrieved memory into canonical form
- `map/dream` — process memory into summary/log updates

## 5. Examples

### Example 1

**Prompt:** What was said about the prior decision?
**Outcome:** Returns Summary and Memory Log matches as structured context.
