# AGENTS.md Instruction-Section Contract

## Purpose

Define where durable instructions for agents belong in an `AGENTS.md` file without prescribing broader document review or organization.

## Required Shape

Use `# Instructions` as the parent section for agent directives.

Within `# Instructions`, use these directive sections when applicable:

- `## Rules` holds concise, imperative requirements: things an agent must do.
- `## Constraints` holds concise prohibitions or approval gates: things an agent must not do, or may do only with approval.

A directive section is optional. Create it only when it contains at least one applicable directive. Do not create an empty section or a placeholder heading.

Other subsections are allowed under `# Instructions`. This contract does not prescribe their names, ordering, or contents.

## Adding Lessons

Record a durable lesson as one concise directive in the applicable section:

- Add a required behavior to `## Rules`.
- Add a prohibition or approval gate to `## Constraints`.

Do not create a separate `Lessons` section. Do not move, consolidate, deduplicate, rewrite, or remove existing directives as part of adding a lesson.

## Directive Quality

Each directive must be:

- Concrete and actionable for an agent.
- Imperative and concise.
- Durable rather than incident-specific.
- Scoped to the directory governed by that `AGENTS.md`.

## Out of Scope

This contract does not define document-wide compression, movement, ordering, consolidation, review checklists, nested-directory inheritance, or conflict precedence.
