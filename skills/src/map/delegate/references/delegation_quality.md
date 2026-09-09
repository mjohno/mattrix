# Delegation Quality Checklist

Use this checklist to check or improve a delegation request.

## Task

- [ ] The delegated action is one bounded outcome.
- [ ] The objective states what success means.
- [ ] The task does not include unrelated parent work.
- [ ] The result can be returned without parent-only context.

## Agent Selection

- [ ] The caller-selected agent is available, if named.
- [ ] Otherwise, the selected agent description fits the action.
- [ ] The selected agent has the required tools and permissions.
- [ ] A general-purpose fallback is used only when it can safely perform the action.
- [ ] If no suitable agent exists, the result is blocked or requests clarification.

## Context

- [ ] The prompt includes the goal, relevant artifacts, and necessary facts.
- [ ] The prompt includes applicable constraints and acceptance criteria.
- [ ] Unrelated conversation content is excluded.
- [ ] Sensitive material is included only when necessary for the task.
- [ ] Missing material is stated as an uncertainty, not invented.

## Persona

- [ ] The persona is named as a skill for the child agent to load.
- [ ] The persona skill is available to the isolated child agent.
- [ ] The prompt does not copy or reinterpret persona instructions.
- [ ] The action remains the task; the persona remains the evaluation lens.

## Invocation

- [ ] The selected plugin can invoke the selected agent.
- [ ] Project-local agents are used only in a trusted project with required approval.
- [ ] The invocation has a defined failure and cancellation result.
- [ ] The delegation does not create persistent state unless the caller requests it.

## Result Contract

- [ ] The prompt states the required output format.
- [ ] Evidence requirements are explicit when evidence is needed.
- [ ] Assumptions, uncertainties, and blocked conditions must be reported.
- [ ] File changes, if allowed, identify affected paths.
- [ ] The parent can check the result without repeating the delegation.

## Decision

A delegation is ready when all applicable items pass. Otherwise, revise the task, context, agent selection, or result contract.
