from __future__ import annotations

from functools import lru_cache
from importlib.resources import files
from typing import Any

import yaml

ROLES = ("coordinator", "worker", "assessor")


@lru_cache
def _source(name: str) -> str:
    return (
        files("stagger_step")
        .joinpath("prompts", name)
        .read_text(encoding="utf-8")
        .strip()
    )


def build_prompt(role: str, context: dict[str, Any]) -> str:
    """Build the complete self-contained prompt for one STEP role invocation."""
    if role not in ROLES:
        raise ValueError(f"unknown STEP role: {role}")
    return "\n\n".join(
        (
            _source("common.md"),
            _source(f"{role}.md"),
            "## Invocation context\n\n```yaml\n"
            + yaml.safe_dump(context, sort_keys=False).strip()
            + "\n```",
            "## Response protocol\n\n"
            f"Call `stagger_step_finalize_{role}` exactly once with one complete "
            f"conforming {role} YAML packet. Do not return the role packet in "
            "assistant text.",
        )
    )
