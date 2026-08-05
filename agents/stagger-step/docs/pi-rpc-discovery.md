# Pi RPC discovery record

Date: 2026-07-28. Runtime: `pi 0.82.1`.

## Executed evidence

A local `pi --mode rpc --no-session --name stagger-step-discovery` JSONL process accepted:

1. `get_state` → `success: true`, an isolated session ID/name, model capability metadata, and non-streaming state.
2. `new_session` → `success: true`, `data.cancelled: false`.
3. `not_a_command` → `success: false`, `error: "Unknown command: not_a_command"`.
4. A separate fresh process accepted `prompt` with a request ID, returned assistant YAML text in `agent_end.messages`, then emitted `agent_settled`. The client must keep stdin open until settlement; closing it immediately after the prompt ends the RPC process before it returns assistant text.

The discovery prompt was `Return exactly this YAML and nothing else: status: ok`; returned text was `status: ok`.

## Adapter decisions

- A fresh process is created per role invocation, named `STEP-<step-slug>-<task-slug>-<role>`. Each transition generates a random UUID for each role when first invoked; that ID is reused only by retry, correction, or clarification calls for that role in the same transition, then cleared before the next transition. The deterministic name and the random session ID preserve same-role context while retaining role isolation. The harness explicitly loads `pi-stagger-step` and supplies its selected `--step-role`. `--harness-session off` uses `--no-session`. The child environment removes `STEP_FILE` and `STAGGER_STEP_*`; no STEP path is supplied to Pi.
- Role output is collected only from the matching `stagger_step_finalize_<role>` `tool_execution_end` result and is accepted only after `agent_settled`. The result is passed through `stagger-step normalize --role <role>` before use. A nonblocking stream wait resets the 120-second idle timeout for every Pi JSONL event and also enforces a 30-minute maximum invocation duration. Missing finalizers, malformed YAML, early closure, and timeout are diagnosable `HarnessError` values, never a state inference.
- The adapter terminates its child before returning a YAML user gate. `abort` is available for cancellation but is not presently exposed by the synchronous CLI.
- Process/RPC failures retry twice with bounded exponential delays (100 ms, 200 ms). Accepted prompts may still fail asynchronously, so a missing settled assistant payload is a failure, not a retry-derived transition.
- `get_state` is permitted diagnostic data only. It is never copied to STEP YAML. Model capability/version mismatch is reported by the harness or can be checked through `get_state`; no compatibility data is persisted.
- Pi documents session persistence, `switch_session`, and `new_session`. The adapter reconnects by supplying its deterministic role UUID on each fresh child process; it does not use RPC `switch_session` or `new_session`. A new user-approved task begins a new process.

## Limits

Pi's public RPC contract does not select a host or container execution environment. That deployment policy is outside stagger-step; the adapter invokes its configured Pi command and never passes a STEP path to Pi.
