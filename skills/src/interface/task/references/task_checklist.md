# Task Checklist

Use this for conformance checks. A task packet passes when every critical item passes.

## Critical

- [ ] Defines one task packet, not a whole plan, spec, or execution log.
- [ ] Includes `TASK_ID`, `Status`, `Goal`, `Source`, `Targets`, `Constraints`, `Verification`, `next_tasks`, and `Log`.
- [ ] `TASK_ID` is stable and referenceable.
- [ ] `Status` is one of `todo`, `doing`, `verifying`, `reviewing`, or `done`.
- [ ] `Goal` describes one useful unit of work.
- [ ] `Source` links to enough originating context to understand the task.
- [ ] Unknown fields are marked honestly instead of invented.
- [ ] `Log` is concise and does not claim verification from formatting alone.

## Optional but Checkable

- [ ] Targets are specific enough for an implementer to start.
- [ ] Verification hints are runnable or evidence-oriented when known.
- [ ] Candidate `next_tasks` preserve branch continuations when present.
