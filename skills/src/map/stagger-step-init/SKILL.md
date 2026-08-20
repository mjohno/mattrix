---
name: stagger-step-init
description: Use when creating one new Stagger Step workflow and its initial owner gate.
metadata:
  type: skill
  category: map
---

# stagger-step-init

Goal: Create one new Stagger Step state file and render its initial owner gate.
Non-Goals: Do not approve gates, run workflow work, edit existing STEP state, or write STEP YAML directly.
Use-When: Use when a user wants to start a Stagger Step workflow for a goal.

## 0. Prerequisites

- The `stagger-step` Python package and its Pi role dependencies are available.
- The user provides a new STEP-file path, or allows the skill to derive one.
- If the user does not provide a goal, use `goal` to propose one and obtain user approval before initialization.

## 1. Inputs

- Goal, or enough context for `goal` to propose one.
- Optional new STEP-file path and change directory.
- Optional lessons, commit mode, packet history, and role model or thinking settings.
- Approval to use inferred paths.

## 2. Processes

1. If no goal is supplied, use `goal`; show its proposed SMART goal and wait for approval.
2. If paths are absent, derive a lower-case kebab-case `<goal-slug>` from the approved goal and propose `tmp/CHANGE-<goal-slug>/STEP-<goal-slug>.yaml` from the checked-out project root.
3. If the change directory is absent, use `tmp/CHANGE-<goal-slug>/`.
4. Show inferred paths and wait for approval before initialization.
5. Stop if the STEP file exists. Do not replace it.
6. Create missing parent directories for the STEP file and change directory with `mkdir -p`.
7. Validate packet history and commit-mode requirements.
8. Run `init` from the checked-out project root. If the STEP file is in the change directory, pass `--change .`; otherwise pass the resolved change directory.
9. Return the rendered initial owner gate. Do not approve it or start a session.

## 3. Outputs

- One new STEP YAML state file and its initial owner gate.
- The selected initialization settings.
- Derived paths and the user approval that authorized them, when paths were inferred.
- A shell-escaped, copyable continuation command: `STEP_FILE=<path> python -m stagger_step.cli session`.

## 4. Next Steps

- `session` — review and respond to Stagger Step owner gates with the returned command.
- `investigate` — diagnose unavailable dependencies or initialization failures.

## 5. Examples

### Example 1

**Prompt:** Initialize a Stagger Step workflow for shipping the search feature in `STEP-search.yaml`.

**Outcome:** Creates `STEP-search.yaml`, renders its first owner gate, and returns a command to continue the session in another terminal.

### Example 2

**Prompt:** Initialize Stagger Step for this initiative. The goal is not defined.

**Outcome:** Uses `goal` to propose a SMART goal, waits for approval, then initializes the workflow.

### Example 3

**Prompt:** Create a Stagger Step workflow to review the checked-out project.

**Outcome:** Proposes `tmp/CHANGE-review-project/STEP-review-project.yaml`, creates the approved change directory, initializes the workflow, and returns its session command.
