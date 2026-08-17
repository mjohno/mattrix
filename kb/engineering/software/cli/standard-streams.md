---
type: Convention
title: Use standard streams for CLI data and diagnostics
description: Keep command data separate from diagnostics to support pipelines.
tags: [cli, unix, ipc]
status: stable
---

# Use standard streams for CLI data and diagnostics

## Convention

Use standard input and standard output for command data. Use standard error for diagnostics, progress, warnings, and logs.

## Rules

- Read piped input from standard input.
- Write the primary result to standard output.
- Write diagnostics and logs to standard error.
- Do not mix human diagnostics with machine-readable standard output.
- Use an explicit file option when the user must select an output or log file.

## Result

Commands can be composed with pipes without parsing progress or log messages.
