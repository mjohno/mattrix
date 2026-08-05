# Change Path Checklist

Use this for conformance checks. A change-path use passes when every critical item passes.

## Critical

- [ ] Defines a change path as a caller-provided local artifact directory for a target plus an intended or possible delta.
- [ ] Keeps selection, identity, lifecycle, access, retention, and coordination with the caller.
- [ ] Does not require or create an identity file, sentinel file, active-change pointer, or fixed directory layout.
- [ ] Uses the change path only for artifacts that support the same target and delta.
- [ ] Keeps each artifact subject to its own contract.
- [ ] Does not treat the change path as an approval record, state store, or security boundary.
- [ ] Excludes deployment, release management, publishing, promotion, and remote environment changes.

## Optional but Checkable

- [ ] The change path is local and temporary.
- [ ] Change-path artifacts are not committed unless caller or repository policy explicitly requires it.
