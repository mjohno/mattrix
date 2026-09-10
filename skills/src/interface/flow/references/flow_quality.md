# Flow Quality Checklist

- [ ] The title identifies the workflow purpose.
- [ ] The flow contains one Mermaid `stateDiagram-v2` graph.
- [ ] The graph contains a start state and an end state.
- [ ] Each activity node has a stable `NODE-###` ID.
- [ ] Each activity node has one matching description.
- [ ] Each description states plainly what the activity should do.
- [ ] The final activity states goal-based completion criteria.
- [ ] The transition to the end state occurs only when the goal criteria are met.
- [ ] Each transition represents an allowed next activity.
- [ ] Return paths exist where rework is needed.
- [ ] The graph is small enough to read without extra explanation.
- [ ] The flow excludes task, worker, state, enforcement, and execution details.
