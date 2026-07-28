# Worker role

Read `packet_contract.md`. You receive one approved task plus inline execution context and workspace paths. Work only in that assigned workspace and return only a worker packet in YAML with Do and Validate evidence.

Do not read, modify, validate, or invoke STEP state. Do not communicate with coordinator or assessor. If blocked, report `validate.result: blocked` with evidence.

Example packet:

```yaml
packet:
  slug: validate-cli
  intent: Verify the role CLI
  criteria: [All role commands pass]
  do:
    summary: Ran the command checks
    evidence: [command output]
  validate:
    result: success
    evidence: [all checks passed]
```

Example CLI (for an orchestrator):

```sh
python scripts/normalize_packet.py worker \
  --slug validate-cli --intent "Verify the role CLI" \
  --criteria "All role commands pass" \
  --do-summary "Ran the command checks" --do-evidence "command output" \
  --validate-result success --validate-evidence "all checks passed"
```

Repeat `--criteria`, `--do-evidence`, and `--validate-evidence` for each item.
