# Change Path Contract

A change path is a caller-provided local directory for artifacts concerning a target plus an intended or possible delta.

```text
change = target + intended or possible delta
change path = local directory for that change's artifacts
```

- Target: the thing being changed, evaluated for change, or prepared for change.
- Delta: what may be added, removed, fixed, revised, replaced, validated, or decided.
- The delta does not need to be fully known. "Determine the necessary fix" is a valid possible delta.

## Ownership

The caller owns change-path selection, identity, lifecycle, access, retention, and coordination. This interface does not infer an active change path, prescribe its parent directory or name, or create it.

## Use

Artifacts at a change path support the same target and delta. They may include specifications, plans, implementation notes, review findings, validation evidence, and supporting files. Each artifact follows its own contract.

A change path is an artifact location, not an approval record, state store, or security boundary. Do not place deployment, release-management, publishing, promotion, or remote-environment work under this contract.

## Locality

A change path is normally local and temporary. It should not be committed by default unless its caller or repository policy explicitly requires otherwise.
