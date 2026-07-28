# STEP role packet contract

The `stagger-step` agent owns STEP state. These packets are role outputs only; they contain no state commands and must not be written by a role.

## Coordinator packet

```yaml
proposed_next_packets:
  - slug: lowercase-kebab-case
    intent: concise outcome
    criteria:
      - observable acceptance criterion
recommendation: lowercase-kebab-case # or null
lessons: [durable lesson]
```

`recommendation`, when present, must name exactly one proposed packet. Slugs must be unique.

## Worker packet

```yaml
packet:
  slug: lowercase-kebab-case
  intent: concise outcome
  criteria: [observable criterion]
do:
  summary: work performed
  evidence: [path, command output, or other evidence]
validate:
  result: success # success | partial | failure | blocked
  evidence: [validation evidence]
```

## Assessor packet

```yaml
current_packet: # the normalized worker packet
  slug: lowercase-kebab-case
  intent: concise outcome
  criteria: [observable criterion]
  do: {summary: work performed, evidence: [evidence]}
  validate: {result: success, evidence: [evidence]}
retro:
  wins: [effective progress]
  issues: [friction, failure, or lack of progress]
  actions: [specific next-step input]
clarification_needed: false
```

The coordinator selects durable lessons from workflow context and assessor actions. The assessor may set `clarification_needed: true` once. The loop, not the assessor, decides whether to invoke one same-role worker follow-up. The assessor must evaluate movement toward the goal and distinguish wins from issues.
