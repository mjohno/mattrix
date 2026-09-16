# Git Commit Checklist

Use this checklist before executing a commit.

- [ ] The repository has staged changes; unstaged changes were not silently included.
- [ ] The staged diff supports the selected Conventional Commit type and optional scope.
- [ ] The header has the required format and an imperative subject of 50 characters or fewer.
- [ ] A breaking change has `!` in the header and a `BREAKING CHANGE:` footer.
- [ ] A body and `Refs:` footer appear only when applicable.
- [ ] The complete message was presented for approval unless the request explicitly authorized immediate execution.
- [ ] The commit succeeded and `git log -1` verified it.
