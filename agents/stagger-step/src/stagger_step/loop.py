from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

from .harness import Harness
from .prompts import build_prompt
from .state import StateError, is_completed, validate_state, validate_task


class TransitionError(StateError):
    pass


def _dedupe(values: list[str]) -> list[str]:
    return list(
        dict.fromkeys(value.strip() for value in values if value.strip())
    )


def _unique_slug(slug: str, used: set[str]) -> str:
    """Keep a slug when available; otherwise advance its trailing integer."""
    if slug not in used:
        return slug
    match = re.fullmatch(r"(.+?)(?:-(\d+))?", slug)
    assert match is not None
    stem, suffix = match.groups()
    index = int(suffix) + 1 if suffix is not None else 1
    candidate = f"{stem}-{index}"
    while candidate in used:
        index += 1
        candidate = f"{stem}-{index}"
    return candidate


def _unique_proposals(
    proposals: Any, recommendation: Any, reserved: set[str]
) -> tuple[Any, Any]:
    """Rename coordinator proposals that collide with current or completed work."""
    if not isinstance(proposals, list):
        return proposals, recommendation
    used = set(reserved)
    normalized: list[Any] = []
    normalized_recommendation = recommendation
    recommendation_updated = False
    for proposal in proposals:
        if not isinstance(proposal, dict) or not isinstance(
            proposal.get("slug"), str
        ):
            normalized.append(proposal)
            continue
        original = proposal["slug"]
        slug = _unique_slug(original, used)
        copied = deepcopy(proposal)
        copied["slug"] = slug
        normalized.append(copied)
        used.add(slug)
        if original == recommendation and not recommendation_updated:
            normalized_recommendation = slug
            recommendation_updated = True
    return normalized, normalized_recommendation


class StepLoop:
    """Own STEP transitions without exposing state files to the harness."""

    def __init__(self, harness: Harness, change_path: str | None = None):
        self.harness = harness
        self.change_path = change_path

    def bootstrap(self, state: dict[str, Any]) -> dict[str, Any]:
        self.harness.begin_transition()
        if state["current"] is not None or state["next"]:
            raise TransitionError("state is already bootstrapped")
        proposed = self._propose(state, actions=[], revision=None)
        proposed["lessons"] = _dedupe([*state["lessons"], *proposed["lessons"]])
        return validate_state(proposed)

    def prepare(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute current work once, then propose follow-up work for a gate."""
        self.harness.begin_transition()
        validate_state(state)
        if state["completed"]:
            raise TransitionError("workflow is already complete")
        if state["current"] is None or is_completed(state["current"]):
            return state
        active = deepcopy(state["current"])
        worker = self.harness.invoke(
            "worker",
            self._prompt("worker", {"task": active, "goal": state["goal"]}),
            task_slug=active["slug"],
        )
        try:
            packet = self._completed_worker_packet(active, worker)
        except StateError as exc:
            worker = self.harness.invoke(
                "worker",
                self._prompt(
                    "worker",
                    {
                        "task": active,
                        "goal": state["goal"],
                        "correction": (
                            f"Your previous worker response was invalid: {exc}. "
                            "Call the worker finalizer with complete valid fields only."
                        ),
                    },
                ),
                task_slug=active["slug"],
                follow_up=True,
            )
            packet = self._completed_worker_packet(active, worker)
        assessor = self._assess(state, active, packet)
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
                task_slug=active["slug"],
                follow_up=True,
            )
            packet = self._completed_worker_packet(active, clarification)
            assessor = self._assess(
                state, active, packet, clarification_used=True
            )
            if assessor["clarification_needed"]:
                raise TransitionError(
                    "assessor requested more than one clarification"
                )
        current = deepcopy(assessor["current_packet"])
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
            (
                step
                for step in state["next"]
                if step["slug"] == state["recommended"]
            ),
            None,
        )
        if current is not None and not is_completed(current):
            raise TransitionError(
                "current step must be assessed before approval"
            )
        if current is None and selected is None:
            raise TransitionError(
                "bootstrap state requires a recommended next step"
            )
        next_state = deepcopy(state)
        if current is not None:
            next_state["history"].append(current)
        next_state["current"] = deepcopy(selected) if selected else None
        if selected is not None:
            next_state["next"] = [
                step
                for step in next_state["next"]
                if step["slug"] != selected["slug"]
            ]
            next_state["recommended"] = None
        else:
            next_state["next"] = []
            next_state["recommended"] = "terminate"
            next_state["completed"] = True
        return validate_state(next_state)

    def gate(self, state: dict[str, Any]) -> dict[str, Any]:
        validate_state(state)
        gate = {
            key: deepcopy(state[key])
            for key in (
                "goal",
                "lessons",
                "history",
                "current",
                "recommended",
                "completed",
            )
        }
        gate["proposals"] = deepcopy(state["next"])
        return gate

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
            task_slug=(state["current"] or {}).get("slug", "bootstrap"),
        )
        if not isinstance(response, dict):
            raise TransitionError("coordinator returned no packet")
        lessons, proposals, recommendation = (
            response.get("lessons"),
            response.get("proposals"),
            response.get("recommendation"),
        )
        reserved = {step["slug"] for step in state["history"]}
        if state["current"] is not None:
            reserved.add(state["current"]["slug"])
        proposals, recommendation = _unique_proposals(
            proposals, recommendation, reserved
        )
        candidate = deepcopy(state)
        candidate["lessons"] = _dedupe(lessons or [])
        candidate["next"] = proposals
        candidate["recommended"] = recommendation
        return validate_state(candidate)

    @staticmethod
    def _completed_worker_packet(
        active: dict[str, Any], worker: Any
    ) -> dict[str, Any]:
        if not isinstance(worker, dict):
            raise StateError("worker response must be a mapping")
        packet = {
            **deepcopy(active),
            "do": worker.get("do"),
            "validate": worker.get("validate"),
        }
        return validate_task(packet, "worker response", True)

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
                    "worker_packet": {"packet": worker},
                    "clarification_already_used": clarification_used,
                },
            ),
            task_slug=active["slug"],
        )
        required = ("retro", "clarification_needed")
        if not isinstance(assessor, dict) or any(
            key not in assessor for key in required
        ):
            raise TransitionError("assessor returned an incomplete response")
        if not isinstance(assessor["retro"], dict) or any(
            not isinstance(assessor["retro"].get(k), list)
            for k in ("wins", "issues", "actions")
        ):
            raise TransitionError("assessor retro is invalid")
        if not isinstance(assessor["clarification_needed"], bool):
            raise TransitionError("assessor clarification flag is invalid")
        return {
            "current_packet": deepcopy(worker),
            "retro": deepcopy(assessor["retro"]),
            "clarification_needed": assessor["clarification_needed"],
        }

    def _prompt(self, role: str, context: dict[str, Any]) -> str:
        return build_prompt(role, context, self.change_path)
