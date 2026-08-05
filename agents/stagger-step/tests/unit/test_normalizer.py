from __future__ import annotations

import pytest
from stagger_step.normalizer import normalize_packet
from stagger_step.state import StateError

COMPLETE = {
    "slug": "validate-cli",
    "intent": "Validate the CLI",
    "criteria": ["all checks pass"],
    "do": {"summary": "Ran checks", "evidence": ["pytest"]},
    "validate": {
        "result": "success",
        "summary": "All checks passed",
        "evidence": ["all passed"],
    },
}


@pytest.mark.parametrize(
    ("role", "candidate"),
    [
        (
            "coordinator",
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
        ("worker", {"packet": COMPLETE}),
        (
            "assessor",
            {
                "current_packet": COMPLETE,
                "retro": {"wins": ["checks run"], "issues": [], "actions": []},
                "clarification_needed": False,
            },
        ),
    ],
)
def test_normalizes_each_role(role, candidate):
    normalized = normalize_packet(role, candidate)

    assert normalized == candidate
    assert normalized is not candidate


def test_rejects_wrong_role_packet():
    with pytest.raises(StateError, match="worker.packet must be a mapping"):
        normalize_packet("worker", {"current_packet": COMPLETE})


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
                "proposed_next_packets": [proposal, proposal],
                "recommendation": "validate-cli",
            },
        )
