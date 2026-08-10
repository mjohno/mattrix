---
name: git-project
description: Use when creating one local Git project branch clone or safely synchronizing one existing clone with its canonical local remote.
metadata:
  type: skill
  category: map
---

# git-project

Goal: Create one branch clone for a local Git project that conforms to the `workspace` interface.
Non-Goals: Do not use worktrees, create initial commits, repair invalid state, or rewrite Git history.
Use-When: Use when one project needs its local bare remote, one branch, and one separate branch clone created or safely synchronized.

## 0. Prerequisites
- Study the `workspace` interface contract.
- Set `WORK_ROOT` to an existing workspace root.
- Install Git and Python 3.13 or later.

## 1. Inputs
- `--project`: Relative project path, such as `team/app`.
- `--branch`: Target branch; default `master`.
- `--from`: Source for a missing target branch; default `master`.
- `--checkout`: Destination clone name; default is `branch` with `/` replaced by `-`.
- `--dry-run`: Report planned changes without changing the workspace.

## 2. Processes
1. Validate all paths and existing Git state before changing it.
2. Stop and report any invalid, conflicting, dirty, or non-fast-forward state; do not repair it.
3. With `--dry-run`, report planned changes without changing the workspace.
4. Create only missing workspace directories, bare remotes, project directories, branches with an existing source, and clones.
5. Configure new clones with a relative `local` remote URL.
6. Fetch, check out, and fast-forward only the requested branch when it exists remotely.
7. Report an unborn branch for a new empty remote without creating a commit.
8. Return Git username and email, or `unset`, for the calling agent to display.

## 3. Outputs
- One canonical bare remote and one separate branch clone when they can be created safely.
- Machine-readable result on stdout and diagnostics on stderr, including planned actions for `--dry-run`.
- Stable exit codes: `0` success and `1` blocked or invalid state.

## 4. Next Steps
- `workspace` — validate the complete workspace layout.
- `check` — check the result against acceptance criteria.
- `investigate` — gather evidence for an unexpected Git state.

## 5. Examples

### Example 1

**Prompt:** Create project `team/app` branch `master`.

**Outcome:** Creates the empty bare remote and `master` clone, then reports its unborn branch state.

### Example 2

**Prompt:** Create branch `foo` from `master` as checkout `bar` for `team/app`.

**Outcome:** Creates `foo` only when `master` exists, then creates the `bar` clone tracking `local/foo`.
