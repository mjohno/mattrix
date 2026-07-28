# Coordinate Checklist

Use this for conformance checks. The `coordinate` skill passes when every critical item passes.

## Critical

- [ ] Defines `coordinate` as a map skill, not a persona, interface, output skill, or artifact contract.
- [ ] Package metadata uses `metadata.type: skill` and `metadata.category: map`.
- [ ] Focuses on orchestration: maintaining coords, choosing next steps, delegating when useful, reconciling results, updating state, and reporting progress.
- [ ] Uses prompt-only coords when no change ID is supplied.
- [ ] Does not create `COORDS.md` in prompt-only mode.
- [ ] With a change ID, reads and writes `./tmp/changes/<change-id>/COORDS.md`.
- [ ] Creates `COORDS.md` only when invoked with a change ID, not merely because a change directory exists.
- [ ] Respects the `change` contract's one-active-change rule and prompt/context-only active selection.
- [ ] Uses existing artifact skills for artifact-specific structure instead of redefining specs, plans, tasks, checks, or reviews.
- [ ] Stops for missing decisions, meaningful ambiguity, approval boundaries, risky changes, or out-of-scope requests.
- [ ] Delegates only when work is independent and useful.
- [ ] Delegation prompts include goal, scope, inputs, expected output, file-change permission, constraints, and stop conditions.
- [ ] Reconciles and verifies delegated results before treating work as advanced.
- [ ] Excludes deployment, release management, publishing, promotion, and remote environment changes.

## Optional but Checkable

- [ ] Uses `assets/coords_template.md` when creating `COORDS.md`.
- [ ] Reports current position, completed moves, evidence, open questions, and next step.
- [ ] Avoids duplicating delegated exploration unless needed for verification or conflict resolution.
