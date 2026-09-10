# Flow Contract

A flow describes allowed progress through a body of work.

## Required Sections

A flow has these sections, in order:

1. Title
2. Graph
3. Nodes

## Title

Use:

```md
# Flow: <name>
```

The name identifies the workflow purpose.

## Graph

Use one Mermaid `stateDiagram-v2` diagram.

The graph must:

- include one start state: `[*]`
- include one end state: `[*]`
- use a stable `NODE-###` ID for each activity node
- show allowed transitions with arrows
- label a transition when its condition is not clear
- show return paths when rework is allowed

The end state shows that the flow can finish. It does not, by itself, prove that the goal is met.

## Nodes

Add `## Nodes` after the graph.

Describe every activity node with a level-three heading that uses its graph ID.

```md
### `NODE-001`
Check the delivered result against the goal. Complete the flow only when available evidence shows that the goal is met.
```

Each description must:

- match one graph node
- state what the activity should do
- state goal-based completion criteria when the node can lead to workflow completion
- use plain, direct language
- describe one coherent activity

Do not describe the start or end state.

## Scope

A flow guides task selection. It does not define task text, worker selection, persistent state, transition enforcement, or execution instructions.
