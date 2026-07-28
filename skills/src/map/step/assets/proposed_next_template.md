# Proposed Next-Step Template

Use this packet in chat only after a successful gate selects a next step. Do not persist or execute it until the user replies with exactly `approved` and `approve` succeeds.

```yaml
proposed:
  slug: "<unique-kebab-case-slug>"
  intent: "<specific outcome for the next step>"
  criteria:
    - "<observable completion criterion>"
```
