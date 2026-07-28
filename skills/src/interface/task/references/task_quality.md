# Task Quality Criteria

Use this for review. Quality is about portability and usefulness.

## Review Questions

1. Can a future implementer understand the task without reopening the whole source artifact?
2. Is the task small enough to execute or verify as one unit?
3. Are source references precise and sufficient?
4. Are targets, constraints, and verification hints useful without being over-specified?
5. Are unknowns visible instead of hidden behind confident guesses?
6. Does `next_tasks` preserve important branch continuations?
7. Is `Log` concise, attributed where useful, and oriented toward handoff?

## Common Findings

- Task goal is actually a multi-step plan.
- Source context is missing or copied too broadly.
- Verification hints are vague or absent despite known checks.
- `done` status appears without supporting evidence.
