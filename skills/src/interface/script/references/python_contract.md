# Python Script Contract

Use when the selected script domain is Python.

## Conventions

1. Assume Python 3.13+ unless the user or project specifies otherwise.
2. Use the standard library unless a third-party package is essential and justified.
3. Follow PEP 8 while prioritizing readability and local consistency.
4. For each required third-party package, document its distribution name and version constraint. Wrap its import in a handler for that package's specific `ModuleNotFoundError`. The error must state the required constraint and an install command. Re-raise errors for other missing modules.
5. Use type hints for function signatures, including return types.
6. Use `argparse` for CLI argument parsing.
7. Use `logging` through a module-level `log` object; diagnostics stream to stderr.
8. Use `print()` only for intentional stdout output.
9. Catch exceptions only when adding context, cleanup, fallback behavior, or clearer user-facing errors.
10. `main()` owns orchestration and returns an integer exit code.
11. Reusable logic belongs in typed helper functions.
12. The `__main__` handler is the final block.

## Optional CLI Features

- `--dry-run` when side effects are meaningful.
- `--log-level` with DEBUG, INFO, WARNING, ERROR, CRITICAL.
- `--test` when using inline test patterns.
