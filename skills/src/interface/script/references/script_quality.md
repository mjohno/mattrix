# Script Quality Criteria

Use this for review. Quality is about safe automation and maintainable execution.

## Review Questions

1. Does the script do exactly what was requested — no more, no less?
2. Are side effects explicit, reversible where possible, and dry-runnable when meaningful?
3. Are logs and errors helpful without polluting machine-readable stdout?
4. Are edge cases handled: empty input, missing files, bad data, repeated runs?
5. Are dependencies justified and easy to install or avoid?
6. Are tests or verification commands credible and runnable?
7. Is the code structured so reusable logic is separate from orchestration?

## Common Findings

- Script mixes user diagnostics into stdout data.
- Dry-run says what would happen but still performs side effects.
- Errors are caught and suppressed without adding value.
- CLI exists but `--help` or validation behavior is unclear.
- Verification only covers the happy path.
