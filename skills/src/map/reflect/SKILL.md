---
name: reflect
description: Use when a session needs a recent retro and referenceable learning-update proposals for agent instructions, project documentation, or durable knowledge.
metadata:
  type: skill
  category: map
---

# reflect

Goal: Turn current-session learning into a retro and routed improvement proposals.
Non-Goals: Do not update files without user approval, implement changes, or update skill packages.
Use-When: A user invokes `/reflect` to capture session learning, reuse or create a recent retro, and identify candidate documentation or knowledge updates.

## 0. Prerequisites

- Current-session context, results, feedback, or actions.
- The `retro` interface.
- User-approved targets before any downstream skill updates files.

## 1. Inputs

- Supplied session context, results, feedback, and existing retro content.
- Optional target paths, documentation scope, or MKF bundle path.
- `references/reflect_routing.md`

## 2. Processes

1. Ignore tool-status messages and skill-load blocks. Check the three most recent meaningful conversation turns for a current-session retro that meets the `retro` contract.
2. If no recent retro exists, use `retro` with `draft` to create one in the prompt. Use its Actions section; do not create a separate task list.
3. Classify each supported learning item as an `AGENTS.md`, `docs/`, or MKF candidate. Assign each item a stable `RFL-###` reference. Mark unsupported targets and unknown paths explicitly.
4. Suggest target paths and downstream skills: `outline` for structure and paths, `draft` for new content, `modify` or `fix` for approved changes, and `record` for an approved MKF target.
5. Incorporate user feedback into the proposals. Keep each `RFL-###` reference stable. Do not update files until the user approves the targets and changes.

## 3. Outputs

- A current-session retro in the prompt, when no recent retro exists.
- Referenceable `RFL-###` learning-update proposals with suggested paths and downstream skills.
- Explicit unknowns, unsupported items, and user decisions needed.

## 4. Next Steps

- `outline` — propose a target structure and file paths.
- `draft` — create new approved content.
- `modify` — apply approved focused changes.
- `fix` — apply approved corrections, when available.
- `record` — create or update one approved MKF concept.

## 5. Examples

### Example 1

**Prompt:** `/reflect`
**Outcome:** Reuses a compliant retro from the last three meaningful turns, or drafts one in the prompt. Returns `RFL-###` proposals for `AGENTS.md`, `docs/`, and MKF targets without updating files.
