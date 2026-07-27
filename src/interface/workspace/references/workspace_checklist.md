# Workspace Checklist

Use this to check a workspace layout. A workspace passes only when every critical item passes.

## Layout Invariants

- [ ] **CRITICAL** `WORK_ROOT` is set and identifies the workspace root being checked.
- [ ] **CRITICAL** The workspace is isolated: no project or remote path is shared with another workspace.
- [ ] **CRITICAL** Every project has exactly one canonical bare remote within the same workspace.
- [ ] **CRITICAL** Each remote's relative organizational path beneath `remotes/` matches its project's relative organizational path beneath `projects/`.
- [ ] **CRITICAL** Each remote directory name `<project>.git` matches its project directory name `<project>`.
- [ ] **CRITICAL** Every project has one primary checkout named for its established primary branch (for example, `main` or `master`).
- [ ] **CRITICAL** Every additional checkout is a sibling of the primary checkout beneath its project directory.

## Bare Remotes

For every directory recognized as a remote beneath `remotes/`:

- [ ] **CRITICAL** It is a valid Git repository (`git -C <remote> rev-parse --git-dir` succeeds).
- [ ] **CRITICAL** It is bare (`git -C <remote> rev-parse --is-bare-repository` returns `true`).

## Project Checkouts

For every checkout directory directly beneath a project directory in `projects/`:

- [ ] **CRITICAL** It is a valid non-bare Git working tree (`git -C <checkout> rev-parse --is-inside-work-tree` returns `true`; `git -C <checkout> rev-parse --is-bare-repository` returns `false`).
- [ ] **CRITICAL** It has a `local` remote.
- [ ] **CRITICAL** The `local` remote URL is a relative path (`git -C <checkout> remote get-url local`).
- [ ] **CRITICAL** The relative `local` URL resolves to the project's corresponding canonical local bare remote beneath `WORK_ROOT`.
- [ ] **CRITICAL** The canonical local bare remote is reachable through `local` (`git -C <checkout> ls-remote local` succeeds).
