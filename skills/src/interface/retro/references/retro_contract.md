# Retro Contract

A retro is a concise, blameless record of a current session. It captures what helped, what reduced effectiveness, and the most valuable improvements to make next.

## Required Shape

```text
# Retro: <session title>

Session: <date, identifier, or bounded session description>
Goal: <intended result>
Evidence: <supplied sources, observations, or None supplied>

## Wins

1. <observable result that helped the session>
   - Evidence: <supporting observation or source>
   - Value: <effect on the goal>

## Issues

1. <system, process, tool, or context problem>
   - Evidence: <supporting observation or source>
   - Effect: <effect on the goal, quality, time, or risk>
   - Contributing conditions: <known conditions, or Unknown>

## Actions

1. <one bounded INVEST task statement>
```

## Contract Rules

- Set `Session` to the current session or state the unknown boundary explicitly.
- State the session `Goal` from supplied context. Do not invent it.
- Include only supported wins and issues. Mark missing evidence or contributing conditions as unknown.
- Describe issues without personal blame. Focus on observable effects and contributing conditions.
- Keep wins and issues distinct. A win describes a helpful result. An issue describes a condition that reduced effectiveness or increased risk.
- Limit actions to one to three high-value improvements.
- Use the `task` skill to create each action as one concise INVEST task statement. Do not add assignees, due dates, follow-up dates, or tracking references to the retro.
- Do not state that an action is complete unless supplied evidence supports the claim.
- Add `Open Questions`, `Assumptions`, `Risks`, or `Decisions Needed` only when supplied context makes them material.
