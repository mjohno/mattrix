from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from .harness import Harness
from .state import StateError, is_completed, validate_state, validate_task

_REFERENCES = (
    Path(__file__).resolve().parents[4]
    / "skills"
    / "src"
    / "map"
    / "step"
    / "references"
)
_ROLE_REFERENCES = {
    role: _REFERENCES / f"{role}.md" for role in ("coordinator", "worker", "assessor")
}
_PACKET_CONTRACT = _REFERENCES / "packet_contract.md"


class TransitionError(StateError):
    pass


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value.strip() for value in values if value.strip()))


class StepLoop:
    """Own STEP transitions without exposing state files to the harness."""

    def __init__(self, harness: Harness):
        self.harness = harness

    def bootstrap(self, state: dict[str, Any]) -> dict[str, Any]:
        if state["current"] is not None or state["next"]:
            raise TransitionError("state is already bootstrapped")
        return self._propose(state, actions=[], revision=None)

    def prepare(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute current work once, then propose follow-up work for a gate."""
        validate_state(state)
        if state["completed"]:
            raise TransitionError("workflow is already complete")
        if state["current"] is None or is_completed(state["current"]):
            return state
        active = deepcopy(state["current"])
        worker = self.harness.invoke(
            "worker", self._prompt("worker", {"task": active, "goal": state["goal"]})
        )
        packet = worker.get("packet") if isinstance(worker, dict) else None
        validate_task(packet, "worker.packet", True)
        if packet["slug"] != active["slug"]:
            raise TransitionError("worker packet does not match current step")
        assessor = self._assess(state, active, worker)
        if assessor["clarification_needed"]:
            clarification = self.harness.invoke(
                "worker",
                self._prompt(
                    "worker",
                    {
                        "task": active,
                        "goal": state["goal"],
                        "clarification": "Provide the missing evidence only.",
                    },
                ),
                follow_up=True,
            )
            packet = (
                clarification.get("packet") if isinstance(clarification, dict) else None
            )
            validate_task(packet, "worker.packet", True)
            assessor = self._assess(
                state, active, clarification, clarification_used=True
            )
            if assessor["clarification_needed"]:
                raise TransitionError("assessor requested more than one clarification")
        current = deepcopy(assessor["current_packet"])
        if current["slug"] != active["slug"]:
            raise TransitionError("assessor packet does not match current step")
        current["retro"] = assessor["retro"]
        prepared = deepcopy(state)
        prepared["current"] = current
        return self._propose(
            prepared, actions=assessor["retro"]["actions"], revision=None
        )

    def revise(self, state: dict[str, Any], feedback: str) -> dict[str, Any]:
        if feedback in {"approved", "break"}:
            raise TransitionError("feedback must not be approved or break")
        prepared = self.prepare(state)
        actions = (
            prepared["current"].get("retro", {}).get("actions", [])
            if prepared["current"]
            else []
        )
        return self._propose(prepared, actions=actions, revision=feedback)

    def approve(self, state: dict[str, Any]) -> dict[str, Any]:
        validate_state(state)
        if state["completed"]:
            raise TransitionError("workflow is already complete")
        current = state["current"]
        selected = next(
            (step for step in state["next"] if step["slug"] == state["recommended"]),
            None,
        )
        if current is not None and not is_completed(current):
            raise TransitionError("current step must be assessed before approval")
        if current is None and selected is None:
            raise TransitionError("bootstrap state requires a recommended next step")
        next_state = deepcopy(state)
        if current is not None:
            next_state["history"].append(current)
        next_state["current"] = deepcopy(selected) if selected else None
        if selected is not None:
            next_state["next"] = [
                step for step in next_state["next"] if step["slug"] != selected["slug"]
            ]
            next_state["recommended"] = None
        else:
            next_state["next"] = []
            next_state["recommended"] = None
            next_state["completed"] = True
        return validate_state(next_state)

    def gate(self, state: dict[str, Any]) -> dict[str, Any]:
        validate_state(state)
        return {
            key: deepcopy(state[key])
            for key in (
                "goal",
                "lessons",
                "history",
                "current",
                "next",
                "recommended",
                "completed",
            )
        }

    def _propose(
        self, state: dict[str, Any], *, actions: list[str], revision: str | None
    ) -> dict[str, Any]:
        prior_gate = {
            key: deepcopy(state[key])
            for key in (
                "goal",
                "lessons",
                "history",
                "current",
                "next",
                "recommended",
                "completed",
            )
        }
        response = self.harness.invoke(
            "coordinator",
            self._prompt(
                "coordinator",
                {
                    "goal": state["goal"],
                    "lessons": state["lessons"],
                    "history": state["history"],
                    "actions": actions,
                    "revision": revision,
                    "prior_gate": prior_gate,
                },
            ),
        )
        if not isinstance(response, dict):
            raise TransitionError("coordinator returned no packet")
        lessons, proposals, recommendation = (
            response.get("lessons"),
            response.get("proposed_next_packets"),
            response.get("recommendation"),
        )
        candidate = deepcopy(state)
        candidate["lessons"] = _dedupe(lessons or [])
        candidate["next"] = proposals
        candidate["recommended"] = recommendation
        return validate_state(candidate)

    def _assess(
        self,
        state: dict[str, Any],
        active: dict[str, Any],
        worker: dict[str, Any],
        clarification_used: bool = False,
    ) -> dict[str, Any]:
        assessor = self.harness.invoke(
            "assessor",
            self._prompt(
                "assessor",
                {
                    "goal": state["goal"],
                    "lessons": state["lessons"],
                    "task": active,
                    "worker_packet": worker,
                    "clarification_already_used": clarification_used,
                },
            ),
        )
        required = ("current_packet", "retro", "clarification_needed")
        if not isinstance(assessor, dict) or any(
            key not in assessor for key in required
        ):
            raise TransitionError("assessor returned an incomplete packet")
        validate_task(assessor["current_packet"], "assessor.current_packet", True)
        if not isinstance(assessor["retro"], dict) or any(
            not isinstance(assessor["retro"].get(k), list)
            for k in ("wins", "issues", "actions")
        ):
            raise TransitionError("assessor retro is invalid")
        if not isinstance(assessor["clarification_needed"], bool):
            raise TransitionError("assessor clarification flag is invalid")
        return assessor

    @staticmethod
    def _prompt(role: str, context: dict[str, Any]) -> str:
        instructions = (
            f"You are the STEP {role}. Read your role contract at "
            f"{_ROLE_REFERENCES[role]} and the shared packet contract at "
            f"{_PACKET_CONTRACT} before responding. Return only a YAML packet "
            "conforming to those contracts. You have no STEP-file access and "
            "cannot contact another role.\n\ncontext:\n"
        )
        return instructions + yaml.safe_dump(context, sort_keys=False)
