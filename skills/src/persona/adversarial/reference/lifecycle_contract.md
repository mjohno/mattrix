# Persona Lifecycle Contract

## Commands

- Recognize only exact commands: `deactivate adversarial` and `reactivate adversarial`.
- A command changes only the named persona.
- Do not infer lifecycle actions from other prose.

## Session State

- Session context tracks whether each persona is active.
- Deactivation stops application of the named persona's perspective, priorities, focus areas, tradeoffs, and output guidance.
- Reactivation restores the named persona.
- State persists until reactivation or a new chat.
- A new chat resets persona activation state.
- Do not create, read, or write a state file.

## Responses

- Successful deactivation: `Deactivated: adversarial.`
- Successful reactivation: `Reactivated: adversarial.`
- Unknown personas, inactive deactivation targets, and active reactivation targets return a short status message.
- Lifecycle commands remain available when `comms` is inactive.
