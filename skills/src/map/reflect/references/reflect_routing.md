# Reflect Routing

## Recent Retro

A recent retro is a current-session retro in one of the three most recent meaningful conversation turns before `/reflect`.

Ignore tool-status messages and skill-load blocks.

A recent retro must contain:

- Session
- Goal
- Evidence
- Wins
- Issues
- Actions

If no recent retro exists, use the `retro` interface with `draft` to create one in the prompt.

## Learning Targets

| Learning type | Suggested target | Downstream skill |
| --- | --- | --- |
| Short-term agent behavior | Nearest applicable `AGENTS.md` | `agentsmd` + `outline`, `draft`, or `modify` |
| Long-term project structure | A specified `docs/` path | `outline`, `draft`, or `modify` |
| Durable reusable knowledge | An explicit MKF concept path | `record` |
| Correction to approved content | Existing target path | `fix`, when available |

## Reflection References

- Assign each learning item a unique `RFL-###` reference.
- Preserve each reference while feedback changes its proposed path, content, or downstream skill.
- Use references for review and approval, for example: `Approve RFL-002 for docs/architecture.md`.

## Boundaries

- Suggest paths. Do not invent existing target files.
- Use the retro Actions section as the action source.
- Do not create a second task list.
- Do not update files unless the user approves the proposed targets and changes.
- Incorporate user feedback before routing or applying a change.
- Do not update skill packages.
- Mark an MKF target as unresolved when no unambiguous bundle path is supplied.
