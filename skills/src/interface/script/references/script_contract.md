# Script Contract

A script is an executable or automatable artifact with one clear purpose, explicit invocation, predictable IO, and safe side-effect behavior.

## Generic Rules

1. One clear purpose; avoid unrelated responsibilities.
2. Invocation surface is explicit: CLI args, environment variables, files, stdin, API, scheduler, or another trigger.
3. Machine-readable output and IPC data use stdout.
4. Human diagnostics, progress, warnings, errors, and logs use stderr.
5. Inputs are validated before irreversible side effects.
6. Side effects are explicit, documented, and dry-runnable when meaningful.
7. Errors explain what failed, why it failed, and how to fix it when possible.
8. Exit/status semantics are documented and stable.
9. Dependencies are minimal, justified, and documented.
10. Verification is runnable and covers happy paths and meaningful failures.

## Domain Selection

- Select Python when the user states Python, path ends in `.py`, a Python shebang/import/runtime is present, or no language is specified.
- Select another domain from explicit language, extension, shebang, runtime clues, or user constraints.
- For unsupported domains, return this generic contract, state that domain-specific refs/assets are unavailable, and hand off to `modify` to add a domain reference.

## Python Profile Summary

- Assume Python 3.13+ unless specified otherwise.
- Prefer standard library.
- Use typed helper functions and a `main() -> int` orchestration function.
- Use `argparse` for CLI parsing.
- Use module-level `logging` for diagnostics to stderr.
- Use `print()` only for intentional stdout data.
- Catch exceptions only when adding useful context, cleanup, fallback behavior, or clearer user-facing errors.

## Minimal Example

```text
Script: cleanup.py
Purpose: Remove generated temp files.
Invocation: python cleanup.py --root PATH --dry-run
Stdout: machine-readable removal summary
Stderr: diagnostics and errors
Verification: python cleanup.py --root sample --dry-run --test
```
