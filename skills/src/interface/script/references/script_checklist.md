# Script Checklist

Use this for conformance checks. A script passes when every applicable critical item passes.

## Critical

- [ ] Has one clear purpose.
- [ ] Invocation surface is explicit.
- [ ] Inputs are validated before irreversible side effects.
- [ ] Machine-readable output uses stdout.
- [ ] Diagnostics, progress, warnings, errors, and logs use stderr.
- [ ] Failure behavior and exit/status semantics are predictable.
- [ ] Dependencies are minimal, justified, and documented with their version constraints.
- [ ] Verification is runnable or clearly described.
- [ ] Local integration tests cover the script's primary behavior across its local components when those interactions exist.
- [ ] Unit tests target meaningful risks not adequately covered by integration tests, such as edge cases, invariants, isolated complexity, or critical regressions.

## Python Critical

- [ ] Required third-party imports handle their specific `ModuleNotFoundError`, name the required version constraint, and give an install command.
- [ ] `main()` owns orchestration and returns an integer exit code.
- [ ] Reusable logic lives in typed helper functions.
- [ ] `argparse` is used for CLI parsing when a CLI exists.
- [ ] `logging` is used for diagnostics rather than stdout prints.
- [ ] `__main__` handler is the final block.

## Quality

A failed Quality item produces a `Partial` result. It does not fail conformance.

- [ ] The script does exactly what was requested, no more and no less.
- [ ] Side effects are explicit, reversible where possible, and dry-runnable when meaningful.
- [ ] Logs and errors are helpful without polluting machine-readable stdout.
- [ ] Errors are surfaced with useful context rather than silently suppressed.
- [ ] Edge cases such as empty input, missing files, bad data, and repeated runs are handled.
- [ ] Dependencies are justified, version-constrained, and easy to install or avoid; missing required packages give an install command.
- [ ] Local integration tests cover primary user-visible behavior across the script's local components.
- [ ] Unit tests are limited to meaningful risks that integration tests do not adequately cover, such as edge cases, invariants, isolated complexity, or critical regressions.
- [ ] Tests or verification commands are credible and runnable.
- [ ] Verification covers relevant non-happy-path behavior.
- [ ] Reusable logic is separate from orchestration.
- [ ] A CLI, when present, has clear `--help` and validation behavior.
