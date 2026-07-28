# Script Checklist

Use this for conformance checks. A script passes when every applicable critical item passes.

## Critical

- [ ] Has one clear purpose.
- [ ] Invocation surface is explicit.
- [ ] Inputs are validated before irreversible side effects.
- [ ] Machine-readable output uses stdout.
- [ ] Diagnostics, progress, warnings, errors, and logs use stderr.
- [ ] Failure behavior and exit/status semantics are predictable.
- [ ] Dependencies are minimal, justified, and documented.
- [ ] Verification is runnable or clearly described.

## Python Critical

- [ ] `main()` owns orchestration and returns an integer exit code.
- [ ] Reusable logic lives in typed helper functions.
- [ ] `argparse` is used for CLI parsing when a CLI exists.
- [ ] `logging` is used for diagnostics rather than stdout prints.
- [ ] `__main__` handler is the final block.
