from __future__ import annotations

import pytest
from stagger_step.normalizer import normalize_packet
from stagger_step.state import StateError


@pytest.mark.parametrize(
    ("role", "candidate", "expected"),
    [
        (
            "coordinator",
            {
                "lessons": ["Keep evidence"],
                "proposals": [
                    {
                        "slug": "validate-cli",
                        "intent": "Validate the CLI",
                        "criteria": ["all checks pass"],
                    }
                ],
                "recommendation": "validate-cli",
            },
            {
                "lessons": ["Keep evidence"],
                "proposals": [
                    {
                        "slug": "validate-cli",
                        "intent": "Validate the CLI",
                        "criteria": ["all checks pass"],
                    }
                ],
                "recommendation": "validate-cli",
            },
        ),
        (
            "worker",
            {"work": {"summary": "Ran checks", "evidence": ["pytest"]}},
            {"work": {"summary": "Ran checks", "evidence": ["pytest"]}},
        ),
        (
            "validator",
            {
                "validate": {
                    "result": "success",
                    "summary": "All checks passed",
                    "evidence": ["all passed"],
                },
                "clarification_request": None,
            },
            {
                "validate": {
                    "result": "success",
                    "summary": "All checks passed",
                    "evidence": ["all passed"],
                },
                "clarification_request": None,
            },
        ),
        (
            "assessor",
            {
                "retro": {"wins": ["checks run"], "issues": [], "actions": []},
                "clarification_requests": [],
            },
            {
                "retro": {"wins": ["checks run"], "issues": [], "actions": []},
                "clarification_requests": [],
            },
        ),
    ],
)
def test_normalizes_each_role(role, candidate, expected):
    normalized = normalize_packet(role, candidate)

    assert normalized == expected
    assert normalize_packet(role, normalized) == expected
    assert normalized is not candidate


def test_allows_proposal_slug_with_terminate_prefix():
    proposal = {
        "slug": "terminate-xyz-thingy",
        "intent": "Continue delivery",
        "criteria": ["evidence exists"],
    }

    assert (
        normalize_packet(
            "coordinator",
            {
                "lessons": [],
                "proposals": [proposal],
                "recommendation": "terminate-xyz-thingy",
            },
        )["recommendation"]
        == "terminate-xyz-thingy"
    )


def test_rejects_wrong_role_packet():
    with pytest.raises(StateError, match="worker.work must be a mapping"):
        normalize_packet("worker", {"current_packet": {}})


@pytest.mark.parametrize(
    ("role", "candidate", "message"),
    [
        (
            "worker",
            {
                "work": {"summary": "implemented", "evidence": []},
                "validate": {
                    "result": "success",
                    "summary": "forbidden",
                    "evidence": [],
                },
            },
            "worker packet must contain only work",
        ),
        (
            "validator",
            {
                "do": {"summary": "forbidden", "evidence": []},
                "validate": {
                    "result": "success",
                    "summary": "checked",
                    "evidence": [],
                },
                "clarification_request": None,
            },
            "validator packet must contain validate and clarification_request",
        ),
    ],
)
def test_rejects_cross_role_packet_fields(role, candidate, message):
    with pytest.raises(StateError, match=message):
        normalize_packet(role, candidate)


def test_rejects_worker_owned_fields_in_coordinator_proposals():
    with pytest.raises(StateError, match="non-task fields: validate, work"):
        normalize_packet(
            "coordinator",
            {
                "lessons": [],
                "proposals": [
                    {
                        "slug": "validate-cli",
                        "intent": "Validate the CLI",
                        "criteria": ["all checks pass"],
                        "work": {
                            "summary": "not coordinator work",
                            "evidence": [],
                        },
                        "validate": {
                            "result": "success",
                            "summary": "not coordinator work",
                            "evidence": [],
                        },
                    }
                ],
                "recommendation": "validate-cli",
            },
        )


def test_rejects_duplicate_coordinator_proposals():
    proposal = {
        "slug": "validate-cli",
        "intent": "Validate the CLI",
        "criteria": ["all checks pass"],
    }
    with pytest.raises(StateError, match="duplicate slugs"):
        normalize_packet(
            "coordinator",
            {
                "lessons": [],
                "proposals": [proposal, proposal],
                "recommendation": "validate-cli",
            },
        )
