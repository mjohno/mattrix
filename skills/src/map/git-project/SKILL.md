---
name: git-project
description: Use when creating one local Git project branch clone or safely synchronizing one existing clone with its canonical local remote.
metadata:
  type: skill
  category: map
---

# git-project

Goal: Create one branch clone for a Git project that conforms to the `workspace` interface.
Non-Goals: Do not use worktrees, create initial commits, push branches, repair invalid state, or rewrite Git history.
Use-When: Use when one project needs its local bare remote and branch clone, or a remote clone with a new local branch.

## 0. Prerequisites
- Study the `workspace` interface contract.
- Set `WORK_ROOT` to an existing workspace root.
- Install Git and Python 3.13 or later.

## 1. Inputs
- `--project`: Relative project path, such as `team/app`.
- `--branch`: Target branch; default `master`.
- `--from`: Source for a missing target branch; default `master`.
- `--checkout`: Destination clone name in local-remote mode; default is `branch` with `/` replaced by `-`.
- `--remote`: Clone this remote, create a new local `--branch` from `--from`, and do not push. This mode cannot use `--checkout`; the destination name is the normalized branch name.
- `--dry-run`: Report planned changes without changing the workspace.

## 2. Processes
1. Validate all paths and existing Git state before changing it.
2. Stop and report any invalid, conflicting, dirty, or non-fast-forward state; do not repair it.
3. With `--dry-run`, report planned changes without changing the workspace.
4. Create only missing workspace directories, bare remotes, project directories, branches with an existing source, and clones.
5. In `--remote` mode, clone `--from` and create the new local `--branch` without changing the remote.
6. Configure local-remote-mode clones with a relative `local` remote URL.
7. Fetch, check out, and fast-forward only the requested branch when it exists remotely in local-remote mode.
8. Normalize `/` in checkout names to `-`, and return the normalized name and resolved path.
9. Report an unborn branch for a new empty local remote without creating a commit.
10. Return Git username and email, or `unset`, for the calling agent to display.

## 3. Outputs
- One canonical bare remote and one separate branch clone, or one remote clone with a new local branch, when they can be created safely.
- Machine-readable result on stdout and diagnostics on stderr, including the normalized checkout name and planned actions for `--dry-run`.
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

**Prompt:** Clone `https://example.invalid/team/app.git` and create branch `feature/idea` from `master` for `team/app`.

**Outcome:** Creates the local `feature/idea` branch without pushing it, in checkout `feature-idea`.
