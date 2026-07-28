from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from typing import Any


_REFERENCES = Path(__file__).resolve().parents[4] / "skills" / "src" / "map" / "step" / "references"
_ROLE_REFERENCES = {
    "coordinator": _REFERENCES / "coordinator.md",
    "worker": _REFERENCES / "worker.md",
    "assessor": _REFERENCES / "assessor.md",
}
_PACKET_CONTRACT = _REFERENCES / "packet_contract.md"
from .harness import Harness, HarnessError
from .state import StateError, validate_gate, validate_state, validate_task

class TransitionError(StateError): pass

def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value.strip() for value in values if value.strip()))

class StepLoop:
    """The sole transition authority. The harness receives data, never state access."""
    def __init__(self, harness: Harness): self.harness = harness

    def render_gate(self, state: dict[str, Any], *, revision: str | None = None, prior_gate: dict[str, Any] | None = None) -> dict[str, Any]:
        validate_state(state)
        if state["completed"]: raise TransitionError("workflow is already complete")
        if state["active_packet"] is None:
            if state["history"]: raise TransitionError("state has completed work but no active packet; use terminal approval")
            proposal = self._coordinator(state, actions=[], revision=revision, prior_gate=prior_gate)
            return self._gate(state, None, proposal["lessons"], proposal)
        return self._execute_and_assess(state, revision=revision, prior_gate=prior_gate)

    def _execute_and_assess(self, state: dict[str, Any], *, revision: str | None, prior_gate: dict[str, Any] | None) -> dict[str, Any]:
        active = deepcopy(state["active_packet"])
        worker = self.harness.invoke("worker", self._prompt("worker", {"task": active, "goal": state["goal"]}))
        packet = worker.get("packet") if isinstance(worker, dict) else None
        validate_task(packet, "worker.packet", True)
        if packet["slug"] != active["slug"]: raise TransitionError("worker packet does not match active task")
        assessor = self._assess(state, active, worker)
        if assessor.get("clarification_needed"):
            clarification = self.harness.invoke("worker", self._prompt("worker", {"task": active, "goal": state["goal"], "clarification": "Provide the missing evidence only."}), follow_up=True)
            packet = clarification.get("packet") if isinstance(clarification, dict) else None
            validate_task(packet, "worker.packet", True)
            assessor = self._assess(state, active, clarification, clarification_used=True)
            if assessor.get("clarification_needed"): raise TransitionError("assessor requested more than one clarification")
        current = deepcopy(assessor["current_packet"])
        if current["slug"] != active["slug"]: raise TransitionError("assessor packet does not match active task")
        current.update({"outcome": assessor["outcome"], "retro": assessor["retro"]})
        proposal = self._coordinator(state, actions=assessor["retro"]["actions"], revision=revision, prior_gate=prior_gate)
        return self._gate(state, current, proposal["lessons"], proposal)

    def _assess(self, state: dict[str, Any], active: dict[str, Any], worker: dict[str, Any], clarification_used: bool = False) -> dict[str, Any]:
        assessor = self.harness.invoke("assessor", self._prompt("assessor", {"goal": state["goal"], "lessons": state["lessons"], "task": active, "worker_packet": worker, "clarification_already_used": clarification_used}))
        required = ("current_packet", "outcome", "retro", "clarification_needed")
        if not isinstance(assessor, dict) or any(key not in assessor for key in required): raise TransitionError("assessor returned an incomplete packet")
        # shared contract validation without importing the skills-domain script
        validate_task(assessor["current_packet"], "assessor.current_packet", True)
        if assessor["outcome"] not in {"progressed", "partial", "blocked", "failed"}: raise TransitionError("assessor outcome is invalid")
        if not isinstance(assessor["retro"], dict) or any(not isinstance(assessor["retro"].get(k), list) for k in ("wins", "issues", "actions")): raise TransitionError("assessor retro is invalid")
        if not isinstance(assessor["clarification_needed"], bool): raise TransitionError("assessor clarification flag is invalid")
        return assessor

    def _coordinator(self, state: dict[str, Any], *, actions: list[str], revision: str | None, prior_gate: dict[str, Any] | None, lessons: list[str] | None = None) -> dict[str, Any]:
        response = self.harness.invoke("coordinator", self._prompt("coordinator", {"goal": state["goal"], "lessons": lessons if lessons is not None else state["lessons"], "history": state["history"], "actions": actions, "revision": revision, "prior_gate": prior_gate}))
        if not isinstance(response, dict): raise TransitionError("coordinator returned no packet")
        proposed = response.get("proposed_next_packets")
        candidate = {"goal": state["goal"], "lessons": response.get("lessons"), "current_packet": None, "proposed_next_packets": proposed, "recommendation": response.get("recommendation")}
        validate_gate(candidate)
        return response

    def _gate(self, state: dict[str, Any], current: dict[str, Any] | None, lessons: list[str], proposal: dict[str, Any]) -> dict[str, Any]:
        gate = {"goal": state["goal"], "lessons": lessons, "current_packet": current, "proposed_next_packets": proposal["proposed_next_packets"], "recommendation": proposal.get("recommendation")}
        return validate_gate(gate)

    @staticmethod
    def _prompt(role: str, context: dict[str, Any]) -> str:
        import yaml
        try:
            role_reference = _ROLE_REFERENCES[role]
        except KeyError as exc:
            raise TransitionError(f"unknown STEP role: {role}") from exc
        return (
            f"You are the STEP {role}. Read your role contract at {role_reference} "
            f"and the shared packet contract at {_PACKET_CONTRACT} before responding. "
            "Return only a YAML packet conforming to those contracts. You have no "
            "STEP-file access and cannot contact another role.\n\ncontext:\n"
            + yaml.safe_dump(context, sort_keys=False)
        )

    def approve(self, state: dict[str, Any], gate: dict[str, Any], user_input: str) -> dict[str, Any]:
        validate_state(state); validate_gate(gate)
        if user_input != "approved": raise TransitionError("only exact 'approved' can change STEP state")
        if gate["goal"] != state["goal"]: raise TransitionError("gate goal does not match STEP state")
        if state["completed"]: raise TransitionError("workflow is already complete")
        current, active = gate["current_packet"], state["active_packet"]
        if current is None and active is not None: raise TransitionError("gate omits the active packet")
        if current is not None:
            if active is None or current["slug"] != active["slug"]: raise TransitionError("gate current packet does not match active state")
        selected = next((p for p in gate["proposed_next_packets"] if p["slug"] == gate["recommendation"]), None)
        next_state = deepcopy(state)
        if current is not None:
            next_state["history"].append(current)
        next_state["lessons"] = _dedupe(gate["lessons"])
        next_state["active_packet"] = selected
        next_state["completed"] = selected is None
        return validate_state(next_state)

    def revise(self, state: dict[str, Any], gate: dict[str, Any], user_input: str) -> dict[str, Any]:
        """Return a fresh gate; never mutate state for revisions or break."""
        validate_state(state); validate_gate(gate)
        if user_input == "approved": raise TransitionError("use approve for exact approval")
        if user_input == "break": return {"outcome": "paused", "changed": False}
        # At a user gate, revisions only replace the displayed lesson/proposal advice.
        proposal = self._coordinator(state, actions=[], revision=user_input, prior_gate=gate, lessons=gate["lessons"])
        return self._gate(state, gate["current_packet"], proposal["lessons"], proposal)
