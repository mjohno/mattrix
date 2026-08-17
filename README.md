# Mattrix

Mattrix is Matt's agentic operating engine: reusable skills, an OKF knowledge-base implementation, and deterministic agents.

## Domains

| Domain | Responsibility |
| --- | --- |
| `skills/` | Reusable skill packages, documentation, and the passive MKF contract at `skills/src/interface/knowledge-base/`. |
| `kb/` | MKF implementation and KB-specific documentation. |
| `agents/` | Agent products. `stagger-step` is the first product; `agents/rfc/` is intentionally deferred. |
| `editors/` | Editor configuration. The initial Neovim configuration is documented in [`editors/nvim/README.md`](editors/nvim/README.md). |

Dependencies flow from `agents` and `kb` to `skills`. No skill or KB component depends on an individual agent.

`agents/stagger-step` owns STEP state, deterministic transitions, and user gates. Pi.dev is a replaceable execution harness behind that agent's adapter; it is not a STEP-state authority.

Mattrix does not store business data, business-domain knowledge, or production application data.

## Docker image

Build the local Docker image, tagged `mattrix:latest`:

```sh
python3 make.py docker-build
```

Pass `--quiet` to suppress successful-build output:

```sh
python3 make.py docker-build --quiet
```

## Python quality workflow

Install the shared Python quality-tool set before running its checks:

```sh
python make.py quality-install
```

Run the complete root quality gate for every future Python change:

```sh
python make.py quality
```

`quality` runs these four configured commands in order:

1. `python make.py format-check` — verify Black formatting without changing files.
2. `python make.py ruff` — lint and check import ordering.
3. `python make.py pylint` — run correctness-focused linting.
4. `python make.py mypy` — run strict static type checking.

Use `python make.py format` to apply Black formatting while iterating. Root
`pyproject.toml` centralizes the configuration for all four tools. The checks
target `agents/`, root `make.py`, and `skills/**/scripts/*.py`; they exclude
generated paths and virtual-environment paths, including Git and tool caches,
`.venv`, `tmp`, build, and distribution artifacts. Root quality validation is
required for every future Python change.

Validation evidence: after this documentation update, all four root commands
(`python make.py format-check`, `python make.py ruff`, `python make.py pylint`,
and `python make.py mypy`) passed, as did `python make.py quality --quiet`.
Their captured outputs are `/tmp/mattrix-format-check.out`,
`/tmp/mattrix-ruff.out`, `/tmp/mattrix-pylint.out`, `/tmp/mattrix-mypy.out`,
and `/tmp/mattrix-quality.out`, respectively.
