---
name: dream
description: Use when memory needs end-to-end cleanup, compression, or summary rewriting.
metadata:
  type: skill
  category: map
  capabilities:
    - memory
---
# dream

Goal: Compose the end-to-end memory cleanup workflow.
Non-Goals: Knowledge-base recording or unrelated file orchestration.
Use-When: The user wants memory summarized, compressed, or cleaned.

## 0. Prerequisites
- A resolved memory file
- The `interface/memory` contract
- The `remember`, `learn`, `interface/memory`, and `memorize` skills

## 1. Inputs
- The full memory file
- Retrieved memory context
- Candidate summary updates
- Approval context for destructive summary rewrites

## 2. Processes
1. Read and follow the `interface/memory` contract.
2. Process the entire memory file every time, not only entries since the last breadcrumb.
3. Read memory via `remember`.
4. Reduce via `learn`.
5. Shape summary updates using the `interface/memory` summary contract.
6. Write back summary/log updates to the memory file.
7. Treat `# Summary` as the durable memory record.
8. Require user approval for full `# Summary` rewrites, especially when deleting specific existing Summary items or resolving contradictions.
9. Present summary rewrite approvals as a git diff-style patch.
10. Allow routine compression when it mostly appends and deduplicates Memory Log content into Summary.
11. Delete fully processed log entries and leave a breadcrumb comment after compression.
12. Leave new breadcrumbs for the current compression; later runs may remove old breadcrumbs when cleaning the file.
13. Do not call `record`; memory and knowledge base remain uncoupled.
14. Perform direct file edits when required to complete the chain.

## 3. Outputs
- Updated memory file content
- Optional approval patch for Summary rewrites
- Optional compression breadcrumb

## 4. Next Steps
- `memorize` — append additional memory entries when needed
- `remember` — inspect the cleaned memory later

## 5. Examples

### Example 1

**Prompt:** Clean up this memory file.
**Outcome:** Retrieves, reduces, shapes, and writes back updated memory.
