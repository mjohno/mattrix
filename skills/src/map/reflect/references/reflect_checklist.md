# Reflect Checklist

Use this checklist with `output/check` to validate a Reflect result or the Reflect skill definition.

## Critical

- [ ] Reflect has one current-session retro as input.
- [ ] The retro includes Session, Goal, Evidence, Wins, Issues, and Actions.
- [ ] Reflect does not create, revise, or search for a retro.
- [ ] Each learning item is supported by retro evidence or an action.
- [ ] Each learning item has one stable `RFL-###` reference.
- [ ] Each proposal states its short-term target, when applicable.
- [ ] Each long-term-memory candidate states an MKF lookup query.
- [ ] Reflect runs `lookup` before every MKF write.
- [ ] Reflect identifies an existing matching concept before creating a new one.
- [ ] Each promotion status is one of: `not_eligible`, `candidate`, `duplicate`, `promote`, or `defer`.
- [ ] Proposal mode does not modify files.
- [ ] Apply mode changes only explicitly approved `RFL-###` items.
- [ ] `apply all` processes current proposals in displayed order.
- [ ] Apply stops before an unresolved target, ambiguous MKF bundle, or failed lookup, reports the blocking `RFL-###`, and does not apply later items.
- [ ] Each approved short-term update uses `agentsmd` and targets the nearest applicable `AGENTS.md`.
- [ ] Each approved long-term update uses `record`.
- [ ] Each long-term update explicitly requests index rebuilding through `record`.
- [ ] Apply output reports changed paths, lookup results, record validation, and index-rebuild results.
- [ ] Reflect does not update skill packages.

## Quality

- [ ] Each proposal is concise, scoped, and traceable to retro evidence.
- [ ] A short-term directive is scoped to its governing `AGENTS.md`; it does not claim to be always loaded outside that scope.
- [ ] Promotion is proposed only for reusable knowledge that a future query can retrieve.
- [ ] Duplicate knowledge updates an existing concept rather than creating an unnecessary new concept.
- [ ] The proposal order is clear: `agentsmd` → `lookup` → `record` → rebuild indexes.
- [ ] Unresolved paths, uncertainty, and required approvals are explicit.
