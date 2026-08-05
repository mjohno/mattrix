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
                "proposed_next_packets": [
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
            {
                "do": {"summary": "Ran checks", "evidence": ["pytest"]},
                "validate": {
                    "result": "success",
                    "summary": "All checks passed",
                    "evidence": ["all passed"],
                },
            },
            {
                "do": {"summary": "Ran checks", "evidence": ["pytest"]},
                "validate": {
                    "result": "success",
                    "summary": "All checks passed",
                    "evidence": ["all passed"],
                },
            },
        ),
        (
            "assessor",
            {
                "retro": {"wins": ["checks run"], "issues": [], "actions": []},
                "clarification_needed": False,
            },
            {
                "retro": {"wins": ["checks run"], "issues": [], "actions": []},
                "clarification_needed": False,
            },
        ),
    ],
)
def test_normalizes_each_role(role, candidate, expected):
    normalized = normalize_packet(role, candidate)

    assert normalized == expected
    assert normalized is not candidate


def test_rejects_wrong_role_packet():
    with pytest.raises(StateError, match="worker.do must be a mapping"):
        normalize_packet("worker", {"current_packet": {}})


def test_rejects_worker_owned_fields_in_coordinator_proposals():
    with pytest.raises(StateError, match="non-task fields: do, validate"):
        normalize_packet(
            "coordinator",
            {
                "lessons": [],
                "proposals": [
                    {
                        "slug": "validate-cli",
                        "intent": "Validate the CLI",
                        "criteria": ["all checks pass"],
                        "do": {"summary": "not coordinator work", "evidence": []},
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
