---
name: git-commit
description: Produces and executes conventional commit messages for staged changes.
metadata:
  category: output
  capabilities:
    - commit_message_generation
    - git_commit_execution
---

# git-commit

Goal: Generate and execute a git commit message that adheres strictly to the [Conventional Commits](git-commit/references/CONVENTIONAL_COMMITS.md) specification.
Non-Goals: Committing unstaged changes (requires manual staging first), creating merge commits, amends, or rebases, bypassing commit message standards.
Use-When: You need to commit staged changes with automated analysis.

## 0. Prerequisites
- Staged changes in a git repository

## 1. Inputs
- Repository context (current directory is the repo)
- Staged changes (checked via `git status --porcelain`)
- Optional: issue key or specific change description

## 2. Processes
1. **Pre-flight Check**: Run `git status --porcelain` to check the state of the repository. If no changes are staged: inform the user and offer to stage all changes (`git add .`) or exit. If changes are present but not staged: inform the user and ask if they wish to stage them.
2. **Analyze Changes**: Run `git diff --cached` to analyze the staged changes. Determine the **Type** (feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert). Determine the **Scope** (optional, e.g., a module or directory). Detect **Breaking Changes**: Look for API removals, significant structural shifts, or explicit indicators in the diff.
3. **Draft Message**: Construct header as `<type>(<scope>): <subject>`. If a breaking change is detected, append `!` to the header. Write a concise subject line in the imperative mood (< 50 characters). If the change is complex, provide a body summary of what changed and why. If a breaking change was detected, include `BREAKING CHANGE: <description>`. If an issue key is provided or detected, include it as `Refs: <key>`.
4. **Review & Approval**: Present the complete drafted message to the user. Ask for confirmation: `Proceed with this commit? [Y/n/edit]`. If the user's initial request implies immediate execution, skip the manual prompt.
5. **Execute Commit**: Use `git commit -F <temp_file>` or multiple `-m` flags to ensure the full message is correctly preserved. Verify success with `git log -1`.

## 3. Outputs
- Git commit message in the prompt for review
- Executed commit in the repository

## 4. Next Steps
- `step` — continue with the next step after commit
- `modify` with `interface/plan` — update plan status for committed items
- `git-commit` — commit additional changes
- `review` — review the committed changes

## 5. Examples

### Example 1: Basic commit
**Prompt**: "commit my changes"
**Decisions**: Analyzed `git diff --cached` and identified the change as a `feat` type with no scope or breaking changes.
**Outcome**:
```
feat: add user authentication logic
```

### Example 2: Basic commit with issue key
**Prompt**: "commit my changes for ABC-123"
**Decisions**: Identified the issue key `ABC-123` and applied it to the footer using the `Refs:` prefix.
**Outcome**:
```
fix(ui): resolve button alignment in header
Refs: ABC-123
```

### Example 3: Advanced commit (Breaking Change)
**Prompt**: "commit my changes. I'm breaking the API by removing the old login method."
**Decisions**: Detected a breaking change in the diff; appended `!` to the header and added a `BREAKING CHANGE` footer.
**Outcome**: `refactor(auth)!: remove deprecated login method` with body and `BREAKING CHANGE` footer.

**Constraints:** Follow the [Conventional Commits](git-commit/references/CONVENTIONAL_COMMITS.md) standard strictly. Header subject <= 50 characters. Breaking changes marked in both header (`!`) and footer. Do not commit if no changes are staged.
