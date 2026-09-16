# Reflect Routing

## Required Input

Reflect consumes a current-session retro. The retro must contain:

- Session
- Goal
- Evidence
- Wins
- Issues
- Actions

Reflect does not create, revise, or search for retros.

## Learning Routes

Process each supported learning item in this order:

| Order | Learning type | Target | Skill |
| --- | --- | --- | --- |
| 1 | Short-term agent behavior | Nearest applicable `AGENTS.md` | `agentsmd` |
| 2 | Durable reusable knowledge | MKF metadata search | `lookup` |
| 3 | Approved long-term knowledge | Existing or new explicit MKF concept path | `record` with explicit index rebuild |

An `AGENTS.md` update is scoped to its governed directory. Do not describe it as always loaded outside that scope.

## Promotion

A short-term directive is a long-term-memory candidate when it is reusable beyond its current directory, has supporting retro evidence, and can be retrieved by a future query.

Before promotion:

1. Run `lookup`.
2. Mark the item `duplicate` when a matching concept already contains the knowledge.
3. Update the matching concept when appropriate.
4. Create a new concept only when no applicable concept exists.
5. Use `record` with an explicit index-rebuild request.

Use one status for each item:

- `not_eligible`
- `candidate`
- `duplicate`
- `promote`
- `defer`

## Proposal Records

Each record includes:

- Stable `RFL-###` reference
- Supported retro evidence and action
- Proposed `AGENTS.md` path and directive, when applicable
- MKF lookup query
- Proposed concept path or matching concept
- Promotion status
- Required approval

## Apply Mode

Apply only explicitly approved references, for example:

```text
/reflect apply RFL-001 RFL-003
/reflect apply all
```

For each approved item, use this sequence:

```text
agentsmd → lookup → record → rebuild indexes
```

`apply all` approves and applies every current proposal in displayed order. Before writing, stop if any item has an unresolved target, ambiguous MKF bundle, or failed lookup. Report the blocking `RFL-###` reference and apply no later items.

Report paths, lookup matches, record validation, and index-rebuild results.

## Boundaries

- Do not update files in proposal mode.
- Do not invent target paths.
- Do not write an MKF concept before lookup.
- Do not write long-term knowledge without an explicit index rebuild.
- Mark an MKF target unresolved when no unambiguous bundle path exists.
- Do not update skill packages.
