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


def _finalizer(role: str) -> str:
    if role not in ROLES:
        raise ValueError(f"unknown STEP role: {role}")
    return f"stagger_step_finalize_{role}"


def build_prompt(role: str, context: dict[str, Any]) -> str:
    """Build the complete self-contained prompt for one STEP role invocation."""
    finalizer = _finalizer(role)
    return "\n\n".join(
        (
            _source("common.md"),
            _source(f"{role}.md"),
            "## Invocation context\n\n```yaml\n"
            + yaml.safe_dump(context, sort_keys=False).strip()
            + "\n```",
            "## Response protocol\n\n"
            f"Call `{finalizer}` exactly once with one complete "
            f"conforming {role} YAML packet. Do not return the role packet in "
            "assistant text.",
        )
    )


def build_continuation_prompt(role: str) -> str:
    """Nudge an idle role session to finish its outstanding work."""
    finalizer = _finalizer(role)
    return (
        "Continue the current STEP role session from its existing context. "
        "An idle period passed before the session settled. Resume the next "
        "unfinished action. Do not restart, repeat completed work, or expand "
        "scope. When the role work is complete, call "
        f"`{finalizer}` exactly once with the complete conforming {role} YAML "
        "packet. Do not return the packet in assistant text."
    )


def build_finalization_prompt(role: str, error: Exception) -> str:
    """Ask a role to format already-complete work through its finalizer."""
    finalizer = _finalizer(role)
    return (
        "Finalize the current STEP role result from the work already completed "
        "in this session. Do not resume implementation, research, or scope "
        "expansion. Format the complete conforming "
        f"{role} YAML packet and call `{finalizer}` exactly once. Do not return "
        "the packet in assistant text. The prior finalization was not accepted: "
        f"{error}"
    )
