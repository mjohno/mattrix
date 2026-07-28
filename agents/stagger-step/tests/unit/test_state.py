from __future__ import annotations
import pytest
from stagger_step.loop import StepLoop, TransitionError
from stagger_step.state import StateError, create_state, validate_state

TASK = {"slug": "task", "intent": "Task", "criteria": ["done"]}
class NoHarness:
    def invoke(self, *args, **kwargs): raise AssertionError("not expected")
    def close(self): pass

def test_manual_state_rejects_invalid_transition():
    state = create_state("Goal"); state["history"] = [{**TASK, "do":{"summary":"done","evidence":[]}, "validate":{"result":"success","evidence":[]}}]
    with pytest.raises(StateError): validate_state(state)

def test_approval_requires_exact_input():
    state = create_state("Goal")
    gate = {"goal":"Goal", "lessons":[], "current_packet":None, "proposed_next_packets":[TASK], "recommendation":"task"}
    with pytest.raises(TransitionError): StepLoop(NoHarness()).approve(state, gate, "Approved")
