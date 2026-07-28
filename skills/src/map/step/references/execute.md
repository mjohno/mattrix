# Execute a STEP

**Input:** a step that `approve` has already promoted into current STEP state.

1. Read `context`, understand its goal, lessons, intent, and criteria, then do only that current step's work.
```bash
python scripts/step_cli.py --file STEP-<slug>.yaml context
```
2. Record work evidence, validate the result against the intent and criteria, retrospect, and record next-step choices. Before recording a retro, read and apply the [`retro checklist`](retro_checklist.md). These may be separate `record` calls or one batch call:
   ```bash
   python scripts/step_cli.py --file STEP-<slug>.yaml record \
     --do '{summary: "<work done>", evidence: ["<evidence>"]}' \
     --validate '{result: "success|partial|failure", evidence: ["<proof>"]}' \
     --retro '{wins: [], issues: [], actions: []}' \
     --next-steps '[<next-slug>]' \
     --recommendation <next-slug-or-null>
   ```
3. If the exact user response is `break` at a user-response boundary, pause without calling `record` or creating sidecar state merely to capture the pause. On resume, read `context` again and continue the already approved current step.
4. For simple failure, retry within this step and record the attempt. For unclear or blocked failure, record the blocker in `retro`, set `validate.result: failure` or `partial`, and propose one recovery or investigation slug in `next_steps`. Do not create retry, task, status, or sidecar state.
5. Run the approval gate. If it returns errors, correct and re-record the current step; do not propose or promote another step.
   ```bash
   python scripts/step_cli.py --file STEP-<slug>.yaml gate
   ```
6. When the `gate` command succeeds, output its complete YAML directly without summarizing or omitting `current_step` fields, then separately propose the selected next step in chat only using [`proposed_next_template.md`](../assets/proposed_next_template.md). If no next step remains, record `--next-steps '[]' --recommendation null`, gate, and offer final sign-off. A later revision at that terminal gate may add a next choice through `record` and a fresh gate.

**Outputs:** recorded current-step outcome, fresh successful gate YAML, and either one chat-only proposal or a terminal state.

**Next mandatory phase:** Proceed to [`gate.md`](gate.md) before presenting or handling the gate.
