# Navigate Routing

## Worker Selection

Select the named worker profile that best matches the task's required role, tools, model, scope, and completion evidence.

Fallback order:

1. Matching named worker profile.
2. `default-worker`.
3. Current session.

A worker profile owns its model, tool list, role instructions, and scope limits.

## NAV Packet

```text
NAV-### — <short outcome title>

Task:
<one task-skill INVEST statement>

Route:
<worker profile, default-worker, or current session>

Reason:
<why this is the next-best outcome>

Context:
- <relevant path, result, feedback, RFL reference, or constraint>

Alternatives not selected:
- <candidate>: <short reason>

Uncertainties:
- <material unknown, or None identified>
```

## Execution Boundary

`navigate` only creates the `NAV-###` recommendation.

`execute NAV-###` performs the work in the current thread.

`delegate NAV-### [guidance]` launches one fresh worker. It receives the complete NAV packet and supplied guidance because it has no shared conversation context.

Do not create worker profiles. Use `outline` to propose a missing profile.
