# Gate a STEP

**Inputs:** fresh successful `gate` YAML and either its separate chat-only proposal or terminal state.

1. Run `gate`. It runs the same complete validation as `lint`, then runs `context` internally and returns that full current context. Do not run a separate `context` command before presenting this gate. Present its successful YAML verbatim, including the complete `current_step` (intent, criteria, `do`, `validate`, `retro`, `next_steps`, and `recommendation`); do not replace it with a summary. Then present any chat-only proposal separately and request review.
2. On exact `approved` with a displayed proposal, promote exactly that proposal before doing any work:
   ```bash
   python scripts/step_cli.py --file STEP-<slug>.yaml approve \
     --slug <exact-approved-slug> \
     --intent "<exact-approved-intent>" \
     --criteria "<exact-approved-criterion>" \
     [--lessons "<durable-lesson>"]
   ```
   `approve` may reject duplicate slugs, an incomplete current step, or a slug absent from prior `next_steps`. Report the error, revise the chat-only proposal, and gate again; never execute after a failed approval. On success, read [`execute.md`](execute.md) and return to execution.
3. On exact `break`, pause immediately. It writes no state and must not promote a proposal, record work, or complete the workflow. On resume, read `context`; if the current step is complete, run `gate` again and either present a fresh chat-only proposal before accepting approval or offer terminal sign-off. If it is incomplete, read [`execute.md`](execute.md) and continue that approved step.
4. On exact `approved` with terminal state, stop. It writes no state. Terminal state requires a successful `gate`, `next_steps: []`, and `recommendation: null`.
5. On another response, treat it as a revision. Revise a proposed next step only in chat. If the gate is terminal and the user asks to add a next step, propose one eligible packet, add its slug to the completed current step with `record --next-steps ... --recommendation ...`, then rerun `gate` and request fresh approval. Do not execute it before exact `approved` and successful `approve`. For more current-step work, read [`execute.md`](execute.md), execute and record it, then gate again. For an explicit current-criteria change, use `record --criteria ...`, rerun as needed, record the attempt, and gate again. Merge durable lessons only through the next successful `approve --lessons`.

**Outputs:** either a successfully promoted current step, a revised chat-only proposal awaiting review, a paused workflow, or a stopped terminal workflow.

**Next mandatory phase:** After successful `approve`, proceed to [`execute.md`](execute.md). If the gate is terminal (`next_steps: []` and `recommendation: null`), accept exact `approved` and stop. Accept exact `break` at any gate to pause.
