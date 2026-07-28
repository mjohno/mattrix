# Process Scenario Quality Checklist

Use this checklist when outlining, drafting, modifying, or reviewing a process diagram and run-through scenario prototype.

## Critical
- [ ] States the decision the process prototype will inform.
- [ ] Names the workflow, handoff, state, or boundary assumption being tested.
- [ ] Identifies actors, systems, inputs, outputs, and triggering conditions.
- [ ] Provides at least one run-through scenario with concrete starting conditions.
- [ ] Includes a Mermaid diagram that matches the written scenario.
- [ ] Shows decision points, handoffs, error paths, or alternate branches when relevant.
- [ ] Defines validation signals, such as reviewers tracing the flow without contradiction.
- [ ] Defines failure signals, such as missing owner, missing data, impossible transition, or ambiguous state.
- [ ] Lists omitted implementation details.
- [ ] Ends with a next decision.

## Quality
- [ ] Uses the simplest Mermaid diagram type that explains the process.
- [ ] Avoids modeling every edge case unless it affects the decision.
- [ ] Keeps actor/system names consistent across text and diagram.
- [ ] Includes one happy path and one stress path when useful.
- [ ] Can be reviewed asynchronously without facilitator explanation.
