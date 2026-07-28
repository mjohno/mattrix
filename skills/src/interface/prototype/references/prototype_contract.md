# Prototype Contract

A prototype is a deliberately low-fidelity artifact for cheaply validating an assumption, interaction, process, contract, or structure before heavier work.

## Required Framing

Every prototype should identify:

- Decision the prototype informs.
- Riskiest assumption being tested.
- Audience/context.
- Scope and omitted work.
- Validation signals.
- Failure signals.
- Next decision after validation.

## Profiles

| Profile | Use When | Template | Quality Checklist |
| --- | --- | --- | --- |
| `tabletop-roleplay` | Human coordination, service interactions, incident response, support flows, policy, or operational readiness. | `assets/tabletop_roleplay_template.md` | `references/tabletop_roleplay_quality_checklist.md` |
| `ui-mockup` | UI comprehension, task flow, information architecture, visual hierarchy, or interaction expectations. | `assets/ui_mockup_template.html` | `references/ui_mockup_quality_checklist.md` |
| `process-scenario` | Process logic, handoffs, states, run-through scenarios, system boundaries, or operational sequence. | `assets/process_scenario_template.md` | `references/process_scenario_quality_checklist.md` |
| `api-contract-stub` | Integration shape, request/response semantics, error behavior, auth expectations, or consumer/provider alignment. | `assets/api_contract_stub_template.yaml` | `references/api_contract_stub_quality_checklist.md` |
| `data-layout-structure` | Data shape, fields, relationships, constraints, examples, imports/exports, or downstream usability. | `assets/data_layout_structure_template.md` | `references/data_layout_structure_quality_checklist.md` |

## Selection Rules

- If the profile is specified, use it.
- If no profile is specified, choose the best-fit profile from the use case and return the other profiles as course-correction options.
- Keep fidelity intentionally low.
- Templates are starting shapes for consuming skills, not mandatory final output.
- Quality checklists are selected for check/review intent or when validating before spending effort.

## Minimal Example

```text
Use case: Validate partner invite API integration.
Selected profile: api-contract-stub
Course-correction options: ui-mockup, process-scenario, data-layout-structure, tabletop-roleplay
Decision: Whether provider/consumer semantics align before implementation.
```
