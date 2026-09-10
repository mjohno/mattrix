# Rubric Contract

A rubric is a reusable quality standard. It defines concise, referenceable criteria without recording an evaluation of a target.

## Required Shape

```text
# RUBRIC-<slug>: <Title>

## Criteria

### <Domain>

- <RPREFIX>-001: <observable quality criterion>
```

## Rules

- The title starts with `RUBRIC-<slug>`.
- `slug` is lowercase kebab-case and identifies the rubric.
- Each criterion has a stable, unique ID in the form `<RPREFIX>-<three-digit sequence>`.
- Numbering starts at `001` independently for each prefix.
- A criterion states one clear quality condition that a reviewer can evaluate without guessing.
- Use only domains relevant to the rubric purpose.
- Keep criteria concise and avoid duplication.
- Preserve criterion IDs across revisions unless the criterion is removed or materially split.
- A rubric defines criteria only. Do not include scope records, questions, answers, result values, evidence, impact, confidence, follow-up work, summaries, or completion state.

## Domain Catalog

Select only applicable domains. Use the assigned prefix for each domain.

| Domain | Prefix | Focus |
| --- | --- | --- |
| Correctness | `RCOR` | Required behavior and intended outcomes. |
| Completeness | `RCMP` | Required outcomes, paths, and deliverables. |
| Clarity | `RCLR` | Clear intent, behavior, and terminology. |
| Conciseness | `RCON` | No unnecessary content or repetition. |
| Simplicity | `RSIM` | No unnecessary complexity. |
| Maintainability | `RMNT` | Safe understanding, change, and support over time. |
| Security | `RSEC` | Protection of confidentiality, integrity, and availability. |
| Performance | `RPER` | Responsiveness, throughput, and resource use. |
| Reliability | `RREL` | Predictable behavior and safe failure recovery. |
| Compatibility | `RCOM` | Required interfaces, environments, versions, and consumers. |
| Accessibility | `RACC` | Use by people with relevant access needs. |
| Observability | `ROBS` | Signals for understanding, diagnosis, and operation. |
| Testability | `RTST` | Efficient, reliable verification. |

## Consumer Rules

- Downstream skills decide how to apply criteria and record any results.
- A rubric can provide criteria to `output/check` and `output/review`.
- A rubric does not prescribe a result scale, evidence format, remediation, or stop condition.

## Minimal Example

```text
# RUBRIC-login-errors: Login Error Quality

## Criteria

### Clarity

- RCLR-001: Each login failure message states a clear recovery action.

### Correctness

- RCOR-001: Each known login failure maps to one consistent user-facing message.
```
