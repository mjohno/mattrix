# Git Project Checklist

Use this checklist to check a `git-project` result.

## Safety

- [ ] The project path is within `WORK_ROOT` and the requested branch and source are explicit.
- [ ] Existing, dirty, conflicting, invalid, or non-fast-forward state stopped the operation without repair.
- [ ] No initial commit, push, history rewrite, worktree, or unrequested branch was created.

## Result

- [ ] The result has the requested canonical bare remote and branch clone, or the requested remote clone and local branch.
- [ ] Local-remote clones use a relative `local` remote URL.
- [ ] Checkout names replace `/` with `-` and the reported path matches the normalized name.
- [ ] The result reports Git identity, branch state, planned actions for dry runs, and the stable exit outcome.
