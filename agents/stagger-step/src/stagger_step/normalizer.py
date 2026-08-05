"""Role-specific JSON finalizer normalization without STEP state access."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .state import StateError, validate_task

ROLES = ("coordinator", "worker", "assessor")
RESULTS = {"success", "partial", "failure", "blocked"}


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise StateError(f"{label} must be a mapping")
    return value


def _strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise StateError(f"{label} must be a list of non-empty strings")
    return value


def normalize_packet(role: str, candidate: Any) -> dict[str, Any]:
    """Validate one role-owned JSON response and return its canonical mapping."""
    if role not in ROLES:
        raise StateError(f"unknown role: {role}")
    packet = _mapping(candidate, role)
    if role == "coordinator":
        _strings(packet.get("lessons"), "coordinator.lessons")
        proposals = packet.get("proposals")
        if not isinstance(proposals, list):
            raise StateError("coordinator.proposals must be a list")
        slugs = []
        for index, proposal in enumerate(proposals):
            label = f"coordinator.proposals[{index}]"
            proposal_mapping = _mapping(proposal, label)
            extra = set(proposal_mapping) - {"slug", "intent", "criteria"}
            if extra:
                raise StateError(
                    f"{label} contains non-task fields: {', '.join(sorted(extra))}"
                )
            slugs.append(validate_task(proposal_mapping, label)["slug"])
        if len(slugs) != len(set(slugs)):
            raise StateError("coordinator.proposals contains duplicate slugs")
        recommendation = packet.get("recommendation")
        if recommendation is not None and recommendation not in slugs:
            raise StateError(
                "coordinator.recommendation must name a proposal or be null"
            )
        return {
            "lessons": deepcopy(packet["lessons"]),
            "proposed_next_packets": deepcopy(proposals),
            "recommendation": recommendation,
        }
    if role == "worker":
        do = _mapping(packet.get("do"), "worker.do")
        validation = _mapping(packet.get("validate"), "worker.validate")
        if not isinstance(do.get("summary"), str) or not do["summary"].strip():
            raise StateError("worker.do.summary is required")
        _strings(do.get("evidence"), "worker.do.evidence")
        if validation.get("result") not in RESULTS:
            raise StateError("worker.validate.result is invalid")
        if (
            not isinstance(validation.get("summary"), str)
            or not validation["summary"].strip()
        ):
            raise StateError("worker.validate.summary is required")
        _strings(validation.get("evidence"), "worker.validate.evidence")
        return {"do": deepcopy(do), "validate": deepcopy(validation)}
    retro = _mapping(packet.get("retro"), "assessor.retro")
    for key in ("wins", "issues", "actions"):
        _strings(retro.get(key), f"assessor.retro.{key}")
    if not isinstance(packet.get("clarification_needed"), bool):
        raise StateError("assessor.clarification_needed must be boolean")
    return {
        "retro": deepcopy(retro),
        "clarification_needed": packet["clarification_needed"],
    }
