# Change Checklist

Use this for conformance checks. A change interface/workspace passes when every critical item passes.

## Critical

- [ ] Defines `change` as an interface/noun contract, not a workflow, output artifact, map, or persona.
- [ ] Package metadata uses `metadata.type: interface` and `metadata.category: interface`.
- [ ] Defines a change as a target plus an intended or possible delta.
- [ ] Uses `./tmp/changes/<change-id>/` as the default local workspace path.
- [ ] Verifies the global temporary workspace convention: `./tmp/` is ignored by git before creating or using commit-risking workspace files under `./tmp/changes/`.
- [ ] States that change workspaces are temporary and should not be committed by default.
- [ ] States that only one change is active at a time.
- [ ] Keeps active change selection in prompt/context only; no repository-level active-change pointer file is required or created.
- [ ] Allows arbitrary safe IDs and recommends a lean lowercase hyphenated slug format when choosing an ID.
- [ ] Excludes deployment, release management, publishing, promotion, and remote environment changes.

## CHANGE.md Boundary

- [ ] Keeps `CHANGE.md` limited to identity/title, target, intent, and artifact index.
- [ ] Does not put requirements in `CHANGE.md`.
- [ ] Does not put acceptance criteria in `CHANGE.md`.
- [ ] Does not put implementation steps in `CHANGE.md`.
- [ ] Does not put validation plans in `CHANGE.md`.
- [ ] Does not put release or deployment steps in `CHANGE.md`.
- [ ] Does not put task breakdowns or detailed decisions in `CHANGE.md`.
- [ ] Routes desired end state to `spec`.
- [ ] Routes ordered gap-closing work to `plan`.
- [ ] Routes task packets to `task`.
- [ ] Routes validation to `check`.
- [ ] Routes evaluation findings to `review`.
- [ ] Routes orchestration state to `coordinate` / `COORDS.md` only when `coordinate` is invoked with a change ID.

## Create / Use Triggers

- [ ] Creates or uses a change when there is a target plus intended or possible delta and the user asks to modify, fix, implement, refactor, migrate, redesign, replace, remove, add, or update something.
- [ ] Creates or uses a change for bug investigation with likely follow-up action.
- [ ] Creates or uses a change for multiple artifacts concerning the same target and delta, such as spec plus plan plus tasks.
- [ ] Creates or uses a change when continuing work from an existing change ID.
- [ ] Creates or uses a change for end-to-end local coordination.
- [ ] Creates or uses a change when findings, decisions, or tasks need to be tracked across turns for the same target and delta.

## Non-Triggers

- [ ] Does not create or use a change for one-off answers.
- [ ] Does not create or use a change for vocabulary definitions.
- [ ] Does not create or use a change for pure explanations.
- [ ] Does not create or use a change for generic study with no intended alteration.
- [ ] Does not create or use a change for simple file reads.
- [ ] Does not create or use a change for isolated review with no expected follow-up.
- [ ] Does not create or use a change for direct chat-only proposals.
- [ ] Does not create or use a change for deployment or release coordination.
- [ ] Asks the user before creating a change workspace when the boundary is ambiguous.

## Optional but Checkable

- [ ] Creates `COORDS.md` only when `coordinate` is invoked with a change ID.
- [ ] Uses lowercase hyphenated slugs for agent-chosen change IDs.
