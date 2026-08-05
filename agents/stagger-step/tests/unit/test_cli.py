from __future__ import annotations

import pytest
from stagger_step.cli import parser, select_commit_mode
from stagger_step.state import create_state


@pytest.mark.parametrize("command", ("gate", "session"))
def test_commit_flag_is_rejected_outside_initialization(command):
    with pytest.raises(SystemExit):
        parser().parse_args([command, "--commit"])


def test_disabled_persisted_commit_mode_selects_no_commit_collaborator(
    tmp_path,
):
    state = create_state("Goal", commit_mode=False)

    assert (
        select_commit_mode(state, tmp_path / "STEP-test.yaml", tmp_path, False)
        is None
    )
