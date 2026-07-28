# Task Extraction Rules

Use only when a caller asks to extract a task packet from another artifact.

## From a Plan Item

- Preserve the plan item ID when suitable as the task ID.
- Use the item title as `Goal`, refining only for clarity.
- Copy `Closes`, `Source`, and dependency references into `Source` or `Constraints`.
- Populate `next_tasks` from explicit successor, branch, or follow-up references; otherwise use `unknown` or `none`.
- Do not copy the full Gap Map unless the gap text is required to understand the task.

## From an Annotation

- Reference the annotation ID in `Source`.
- Use the annotation message as the initial `Goal` or `Constraint`.
- Include the file path and nearby symbol/section as `Targets` when known.
- Do not remove or edit the annotation.

## From a Spec or Review Finding

- Preserve artifact IDs such as requirements, acceptance criteria, decisions, or sections.
- Extract the smallest actionable slice.
- Keep future-state intent and technical constraints separate when possible.

## From Direct Instruction

- Infer an ID only if the caller did not provide one.
- Record the user prompt or chat summary in `Source`.
- Mark missing targets, constraints, verification hints, and `next_tasks` as unknown.
