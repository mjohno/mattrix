# Start a STEP

**Inputs:** a goal and a `STEP-<slug>.yaml` path from context or `STEP_FILE`.

1. Start or resume the workflow. For a new workflow, `start` creates the file. For a paused existing workflow, do not restart it: read its context and continue from its persisted current step. To replace only the goal while preserving lessons and steps, use `start --goal "..." --force`.
   ```bash
   python scripts/step_cli.py --file STEP-<slug>.yaml start --goal "..." [--lesson "..."]
   ```
2. Read the current state.
   ```bash
   python scripts/step_cli.py --file STEP-<slug>.yaml context
   ```
3. If `current_step` is incomplete, it is an already approved step: read [`execute.md`](execute.md) and continue it. If `current_step` is complete, run `gate` and present a fresh chat-only proposal from its persisted `next_steps`, or offer terminal sign-off when none remain. If there is no current step, propose exactly one unique kebab-case step in chat only. Do not execute or persist it. Use the [`proposed_next_template.md`](../assets/proposed_next_template.md) packet.
4. Request a gate and wait. On exact `approved`, read [`gate.md`](gate.md), then run `approve` with that exact displayed packet before doing any execution. On exact `break`, pause without changing state. On revision, revise the chat proposal and gate it again. To change the persisted goal, use `start --goal "..." --force`.

**Outputs:** unchanged or initialized STEP state and either a continued approved step, one chat-only proposal with a requested user gate, or terminal sign-off.

**Next mandatory phase:** After successful `approve`, proceed to [`execute.md`](execute.md).
