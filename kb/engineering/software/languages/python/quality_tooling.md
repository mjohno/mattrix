---
type: engineering-standard
title: Python Quality Tooling
description: Shared Ruff and basedpyright policy for Python projects.
tags: [python, ruff, basedpyright, quality]
status: stable
---

# Python Quality Tooling

## Purpose

Use Ruff and basedpyright as the Python quality tools.

## Tool Ownership

- Ruff formats Python code, checks imports, and runs lint rules.
- basedpyright runs Python type checks.
- Do not use separate formatting, linting, or type-checking tools unless a project has a stated need.

## Project Configuration

A project's `pyproject.toml` is the source of truth.

Configure:

- Supported Python version.
- Line length: 80 characters.
- Ruff rules: `E`, `F`, `I`, `UP`, `B`, and `PL`.
- Ruff formatting settings.
- basedpyright type-checking level and exclusions.

Add an ignore only when the project has a reviewed reason.

## Commands

Run these commands from the project directory:

```sh
ruff format .
ruff format --check .
ruff check .
basedpyright
```

Use the project quality command, when one exists, to run all required checks together.

## Scoped Exceptions

Keep exceptions narrow.

- Prefer a fix when a rule improves the code.
- Use per-file exceptions for intentional test literals or established control-flow patterns.
- Document why each exception exists.
- Do not copy legacy linter ignore lists without review.
