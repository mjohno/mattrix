from __future__ import annotations

import pytest
from stagger_step.cli import is_revision_feedback, parser, select_commit_mode
from stagger_step.state import create_state


@pytest.mark.parametrize("command", ("gate", "session"))
def test_commit_flag_is_rejected_outside_initialization(command):
    with pytest.raises(SystemExit):
        parser().parse_args([command, "--commit"])


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", False),
        ("    ", False),
        (" #@%567!  ", False),
        ("5%@!#%", False),
        ("abc", False),
        ("tests", True),
        ("fix 5", True),
    ],
)
def test_revision_feedback_requires_letters_and_more_than_three_characters(
    value, expected
):
    assert is_revision_feedback(value) is expected


def test_init_packet_history_defaults_to_three_and_accepts_a_positive_value():
    assert parser().parse_args(["init", "--goal", "Goal"]).packet_history == 3
    assert (
        parser()
        .parse_args(["init", "--goal", "Goal", "--packet_history", "3"])
        .packet_history
        == 3
    )


def test_disabled_persisted_commit_mode_selects_no_commit_collaborator(
    tmp_path,
):
    state = create_state("Goal", commit_mode=False)

    assert (
        select_commit_mode(state, tmp_path / "STEP-test.yaml", tmp_path, False)
        is None
    )
