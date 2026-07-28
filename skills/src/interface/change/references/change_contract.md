# Change Contract

A change is a temporary local workspace for work that concerns a target thing plus an intended or possible delta to that thing.

```text
change = target + intended or possible delta
```

- Target: the thing being changed, evaluated for change, or prepared for change.
- Delta: what may be added, removed, fixed, revised, replaced, validated, or decided.

The delta does not need to be fully known. "Determine the necessary fix" is a valid possible delta.

## Location

Default root:

```text
./tmp/changes/<change-id>/
```

Artifacts may live under the change directory and should follow their own contracts.

## Identity

Use one safe path-segment ID. Prefer lowercase hyphenated slugs when choosing one. Only one change is active, selected in prompt/context.

Do not create a repository-level active-change pointer file.

## CHANGE.md

`CHANGE.md` identifies the workspace. Keep it shallow:

- Change ID/title
- Target
- Intent
- Artifact index

## Scope

Change workspaces are temporary local working state and should not be committed by default.

Deployment, release management, publishing, promotion, and remote environment changes are out of scope.
