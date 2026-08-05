"""Role-specific STEP packet normalization without STEP state access."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .state import StateError, validate_task

ROLES = ("coordinator", "worker", "assessor")


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
    """Validate one role response and return an isolated canonical mapping."""
    if role not in ROLES:
        raise StateError(f"unknown role: {role}")
    packet = _mapping(candidate, role)
    if role == "coordinator":
        _strings(packet.get("lessons"), "coordinator.lessons")
        proposals = packet.get("proposed_next_packets")
        if not isinstance(proposals, list):
            raise StateError("coordinator.proposed_next_packets must be a list")
        slugs = [
            validate_task(
                proposal, f"coordinator.proposed_next_packets[{index}]"
            )["slug"]
            for index, proposal in enumerate(proposals)
        ]
        if len(slugs) != len(set(slugs)):
            raise StateError(
                "coordinator.proposed_next_packets contains duplicate slugs"
            )
        recommendation = packet.get("recommendation")
        if recommendation is not None and recommendation not in slugs:
            raise StateError(
                "coordinator.recommendation must name a proposed packet or be null"
            )
    elif role == "worker":
        validate_task(packet.get("packet"), "worker.packet", True)
    else:
        validate_task(
            packet.get("current_packet"), "assessor.current_packet", True
        )
        retro = _mapping(packet.get("retro"), "assessor.retro")
        for key in ("wins", "issues", "actions"):
            _strings(retro.get(key), f"assessor.retro.{key}")
        if not isinstance(packet.get("clarification_needed"), bool):
            raise StateError("assessor.clarification_needed must be boolean")
    return deepcopy(packet)
