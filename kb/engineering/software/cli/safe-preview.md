---
type: Convention
title: Provide a dry-run mode for mutating CLI commands
description: Let users inspect intended changes before the command makes them.
tags: [cli, safety]
status: stable
---

# Provide a dry-run mode for mutating CLI commands

## Convention

A CLI command that can change external state should provide `--dry-run` when the intended change can be determined before it is made.

## Behavior

- Do not make target changes.
- Show the actions that the command would take.
- Use the same validation and selection logic as a normal run where practical.
- Make the output clear that it is a preview.
- Do not describe a partial simulation as a complete preview.

## Exceptions

Do not add `--dry-run` when a meaningful preview is not possible or would misrepresent the real operation.
