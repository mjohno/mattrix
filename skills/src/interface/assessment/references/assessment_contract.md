# Assessment Contract

The canonical layout is the [template](../assets/assessment_template.md).

An assessment is a category-based, evidence-backed evaluation artifact. It declares the resource targets being evaluated, records answers to questions about those resources, and preserves uncertainty without acting as a completion-goal or stop-condition contract.

## Scope Rules

- `In Scope` lists the resource groups subject to evaluation.
- `Out of Scope` lists explicit exclusions.
- Do not add a separate target field: scope defines the assessment targets.
- Every question addresses one or more resource groups listed in `In Scope`.

## Question Rules

- Questions use the flat fields `Question`, `Answer`, `Status`, `Evidence found`, `Impact`, `Confidence`, and `Follow-up`.
- A question ID is `Q-<CATEGORY>-<three-digit sequence>`; numbering starts at `001` independently in each category.
- Questions invite a grounded, open-ended answer that establishes the relevant truth or uncertainty for the scoped resources.
- `Status` is one of `Pass`, `Partial`, `Fail`, or `Insufficient evidence`.
- `Impact` and `Confidence` are each one of `High`, `Medium`, or `Low`.
- For `Pass`, `Partial`, and `Fail`, `Evidence found` contains at least one reference in one of these forms: `path:line` or `path:start-end`, `URL#anchor`, or `command — exit code N`.
- Evidence references must not reproduce full evidence text or summarize command output.
- `Insufficient evidence` explicitly states the absence or limitation of available evidence.
- `Follow-up` is a concrete next action or `None`.

## Category Catalog

Use only categories relevant to the declared scope. Category headings use singular Title Case names and the assigned uppercase ID prefix.

| Category | Prefix | Evaluation focus |
|---|---|---|
| Correctness | `COR` | Whether scoped resources satisfy stated requirements and behave as intended. |
| Completeness | `CMP` | Whether all required outcomes, paths, and deliverables are present or explicitly deferred. |
| Clarity | `CLR` | Whether intent, behavior, and terminology can be understood without guessing. |
| Conciseness | `CON` | Whether unnecessary content, repetition, or explanation is absent. |
| Simplicity | `SIM` | Whether unnecessary conceptual, structural, or technical complexity is absent. |
| Maintainability | `MNT` | Whether scoped resources can be safely understood, changed, and supported over time. |
| Security | `SEC` | Whether confidentiality, integrity and availability of relevant assets are protected. |
| Performance | `PER` | Whether applicable responsiveness, throughput, and resource-use expectations are met. |
| Reliability | `REL` | Whether behavior is predictable and recovery or failure is safe under expected fault conditions. |
| Compatibility | `COM` | Whether required interfaces, environments, versions, and consumers are supported. |
| Accessibility | `ACC` | Whether people with relevant access needs can use the scoped resources. |
| Observability | `OBS` | Whether sufficient signals exist to understand, diagnose, and operate the scoped resources. |
| Testability | `TST` | Whether scoped resources can be efficiently and reliably verified. |

## Summary Rules

- The summary groups question IDs by `Pass`, `Partial`, `Fail`, and `Insufficient evidence`.
- The summary identifies the next follow-up actions sorted from highest value to lowest value or `None`.
- Non-passing statuses record uncertainty or gaps; they do not impose a stop condition.

## Consumer Rules

- An assessment can guide `output/review` and `output/check` as their criteria source.
- An assessment is the complete evaluation artifact. A question is one evaluation unit within an assessment.
- Assessment composability, automated execution, and stagger-step completion-goal behavior are outside this contract.
