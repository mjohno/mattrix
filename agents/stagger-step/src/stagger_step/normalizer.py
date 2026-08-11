"""Role-specific JSON finalizer normalization without STEP state access."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .state import StateError, validate_task

ROLES = ("coordinator", "worker", "validator", "assessor")
RESULTS = {"success", "partial", "failure", "blocked"}
CLARIFICATION_TARGETS = {"worker", "validator"}


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


def _validate_packet(value: Any, label: str) -> dict[str, Any]:
    validation = _mapping(value, label)
    if validation.get("result") not in RESULTS:
        raise StateError(f"{label}.result is invalid")
    if (
        not isinstance(validation.get("summary"), str)
        or not validation["summary"].strip()
    ):
        raise StateError(f"{label}.summary is required")
    _strings(validation.get("evidence"), f"{label}.evidence")
    return validation


def _clarification_requests(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list) or len(value) > 2:
        raise StateError(
            "assessor.clarification_requests must contain at most two items"
        )
    requests: list[dict[str, str]] = []
    targets: set[str] = set()
    for index, item in enumerate(value):
        request = _mapping(item, f"assessor.clarification_requests[{index}]")
        if set(request) != {"target", "request"}:
            raise StateError(
                f"assessor.clarification_requests[{index}] must contain target and request"
            )
        target, text = request.get("target"), request.get("request")
        if target not in CLARIFICATION_TARGETS:
            raise StateError(
                f"assessor.clarification_requests[{index}].target is invalid"
            )
        if not isinstance(text, str) or not text.strip():
            raise StateError(
                f"assessor.clarification_requests[{index}].request is required"
            )
        if target in targets:
            raise StateError(
                "assessor.clarification_requests contains duplicate targets"
            )
        targets.add(target)
        requests.append({"target": target, "request": text})
    return requests


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
        if any(slug == "terminate" for slug in slugs):
            raise StateError(
                "coordinator.proposals must not use reserved slug: terminate"
            )
        if recommendation != "terminate" and recommendation not in slugs:
            raise StateError(
                'coordinator.recommendation must name a proposal or be "terminate"'
            )
        return {
            "lessons": deepcopy(packet["lessons"]),
            "proposals": deepcopy(proposals),
            "recommendation": recommendation,
        }
    if role == "worker":
        do = _mapping(packet.get("do"), "worker.do")
        if not isinstance(do.get("summary"), str) or not do["summary"].strip():
            raise StateError("worker.do.summary is required")
        _strings(do.get("evidence"), "worker.do.evidence")
        if set(packet) != {"do"}:
            raise StateError("worker packet must contain only do")
        return {"do": deepcopy(do)}
    if role == "validator":
        validation = _validate_packet(
            packet.get("validate"), "validator.validate"
        )
        clarification = packet.get("clarification_request")
        if clarification is not None and (
            not isinstance(clarification, str) or not clarification.strip()
        ):
            raise StateError(
                "validator.clarification_request must be a non-empty string or null"
            )
        if set(packet) != {"validate", "clarification_request"}:
            raise StateError(
                "validator packet must contain validate and clarification_request"
            )
        return {
            "validate": deepcopy(validation),
            "clarification_request": clarification,
        }
    retro = _mapping(packet.get("retro"), "assessor.retro")
    for key in ("wins", "issues", "actions"):
        _strings(retro.get(key), f"assessor.retro.{key}")
    return {
        "retro": deepcopy(retro),
        "clarification_requests": _clarification_requests(
            packet.get("clarification_requests")
        ),
    }
