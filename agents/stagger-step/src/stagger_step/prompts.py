from __future__ import annotations

from functools import lru_cache
from importlib.resources import files
from typing import Any

import yaml

ROLES = ("coordinator", "worker", "validator", "assessor")


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


def _finalizer_example(role: str) -> str:
    if role == "coordinator":
        return '{"lessons":["durable lesson"],"proposals":[{"slug":"next-task","intent":"bounded outcome","criteria":["observable criterion"]}],"recommendation":"next-task"}'
    if role == "worker":
        return '{"work_summary":"work performed","work_evidence":["evidence"]}'
    if role == "validator":
        return '{"result":"success","validation_summary":"checks performed","validation_evidence":["validation evidence"],"clarification_request":null}'
    return '{"wins":["effective progress"],"issues":["remaining issue"],"actions":["next-step input"],"clarification_requests":[]}'


def _response_protocol(role: str) -> str:
    finalizer = _finalizer(role)
    return (
        "## Response protocol\n\n"
        f"Call `{finalizer}` exactly once with its required typed arguments. "
        "Do not return a role packet in assistant text. For example:\n\n"
        f"`{finalizer}({_finalizer_example(role)})`"
    )


def build_prompt(
    role: str, context: dict[str, Any], change_path: str | None = None
) -> str:
    """Build the complete self-contained prompt for one STEP role invocation."""
    _finalizer(role)
    sections = [_source("common.md"), _source(f"{role}.md")]
    if change_path is not None:
        sections.append(
            "## Change path\n\n"
            "A change path is active for this STEP workflow:\n\n"
            f"`{change_path}`\n\n"
            "Use this directory for artifacts produced by your role for the "
            "approved task, such as plans, implementation notes, review "
            "findings, validation evidence, and supporting files. Reuse "
            "relevant existing artifacts there when they apply.\n\n"
            "The change path is an artifact location, not STEP state or an "
            "approval mechanism. Do not inspect, modify, or validate the "
            "STEP file. Keep artifacts scoped to the approved task and report "
            "relevant artifact paths in your role evidence where the packet "
            "format permits it.\n\n"
            "This path is not a security boundary; continue to follow your "
            "assigned workspace and task-scope constraints."
        )
    sections.extend(
        (
            "## Invocation context\n\n```yaml\n"
            + yaml.safe_dump(context, sort_keys=False).strip()
            + "\n```",
            _response_protocol(role),
        )
    )
    return "\n\n".join(sections)


def build_finalization_prompt(role: str, error: Exception) -> str:
    """Ask a role to format already-complete work through its finalizer."""
    _finalizer(role)
    return (
        "Finalize the current STEP role result from the work already completed "
        "in this session. Do not resume implementation, research, or scope "
        "expansion. "
        + _response_protocol(role)
        + "\n\nThe prior finalization was not accepted: "
        + str(error)
    )
