# Task Contract

A task packet is a portable, self-contained context bundle for one useful unit of implementation, verification, or review work.

## Required Shape

```text
TASK_ID: <stable-id>
Status: todo
Goal: <one clear task goal>
Source:
- <spec/plan/comment/review/prompt/other source>
Targets:
- <file, module, section, or unknown>
Constraints:
- <constraint or unknown>
Verification:
- <hint or unknown>
next_tasks:
- <candidate next task ID, none, or unknown>
Log:
- <concise evidence, comment, handoff note, or unknown>
```

## Rules

- Preserve stable task IDs unless explicitly renamed.
- Prefer source references over copying large context.
- Mark unknowns honestly; do not invent certainty.
- Keep the packet useful outside its original file.
- `next_tasks` is navigation metadata, not a complete dependency graph.
- `Log` may record evidence or handoff notes, but formatting alone is not verification.
- A task packet does not implement, verify, or manage a whole plan.

## Status Values

Use only `todo`, `doing`, `verifying`, `reviewing`, or `done`.

## Minimal Example

```text
TASK_ID: AUTH-2
Status: todo
Goal: Normalize login failure messages.
Source:
- PLAN-login-errors-1
Targets:
- src/auth/login_errors.py
Constraints:
- Preserve existing error codes.
Verification:
- Run auth message tests.
next_tasks:
- unknown
Log:
- Extracted from login error cleanup plan.
```
