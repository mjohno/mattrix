# Mattrix

Mattrix is Matt's agentic operating engine: reusable skills, an MKF knowledge-base implementation, and deterministic agents.

## Domains

| Domain | Responsibility |
| --- | --- |
| `skills/` | Reusable skill packages, documentation, and the passive MKF contract at `skills/src/interface/knowledge-base/`. |
| `kb/` | MKF implementation and KB-specific documentation. |
| `agents/` | Agent products. `stagger-step` is the first product; `agents/rfc/` is intentionally deferred. |

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
