# Flow Quality Checklist

Use this checklist with `flow_contract.md`.

## Critical

- [ ] The flow has a title, one Mermaid `flowchart` diagram, and a `## Nodes` section.
- [ ] The graph has exactly one start node and one end node.
- [ ] Every node has a unique, stable, type-correct ID: `FSTA-###`, `FACT-###`, `FDEC-###`, or `FEND-###`.
- [ ] Each node uses the required process-flow shape for its type.
- [ ] Every activity and decision node in the graph has one matching node description.
- [ ] Each activity description states what it does and when it is complete.
- [ ] Each decision description states the question that determines its outgoing path.
- [ ] Every transition has a clear, observable transition criterion.
- [ ] Each transition into the end node has explicit goal-based completion criteria.
- [ ] Every decision has labeled outgoing outcomes.
- [ ] Decision outcomes are mutually exclusive and cover all expected cases.
- [ ] Each activity or decision failure outcome transitions to a corrective activity or an explicitly defined stopped state.
- [ ] Each corrective activity states which failed criteria it corrects and when correction is complete.
- [ ] Each corrective path returns to the relevant check or decision before the flow can complete.
- [ ] A failure path cannot reach the end node without meeting the failed criterion.
- [ ] The graph has no unintended dead end, unreachable node, or transition to an undefined node.
- [ ] Every allowed rework path is shown in the graph.
- [ ] A threshold criterion defines its check population, required result, and treatment of blocked or unrun checks.

## Quality

- [ ] The flow uses the fewest nodes needed to show the process clearly.
- [ ] Each activity node describes one coherent action.
- [ ] Node names and transition criteria use plain, direct language.
- [ ] Transition criteria state evidence, not subjective intent.
- [ ] Decision nodes exist only where the flow has a real branch.
- [ ] Decision labels are short and describe outcomes, such as `pass` and `fail`.
- [ ] IDs remain stable when node wording changes.
- [ ] The diagram flows in one clear direction where practical.
- [ ] Return paths make rework and retry behavior easy to understand.
- [ ] Completion depends on evidence that the stated goal is met, not only arrival at an end node.
- [ ] The flow does not include task assignment, worker selection, persistent state, or execution instructions.
