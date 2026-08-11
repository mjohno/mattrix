from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, cast

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
        """Run Do, Check, Act, and Plan once for one owner gate."""
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
        do = self._worker_packet(worker)
        validation = self._validate(state, active, do)
        packet = self._completed_packet(active, do, validation)
        assessor = self._assess(
            state, active, packet, clarification_used=False, clarifications=[]
        )
        clarifications: list[dict[str, Any]] = []
        requests = assessor["clarification_requests"]
        if requests:
            clarifications = self._assessor_clarifications(
                state, active, packet, requests
            )
            assessor = self._assess(
                state,
                active,
                packet,
                clarification_used=True,
                clarifications=clarifications,
            )
            if assessor["clarification_requests"]:
                raise TransitionError(
                    "assessor requested more than one clarification round"
                )
        current = deepcopy(packet)
        if clarifications:
            current["clarifications"] = clarifications
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

    def _validate(
        self, state: dict[str, Any], active: dict[str, Any], do: dict[str, Any]
    ) -> dict[str, Any]:
        validator = self.harness.invoke(
            "validator",
            self._prompt(
                "validator",
                {
                    "task": active,
                    "goal": state["goal"],
                    "worker_packet": {"do": do},
                    "clarification_already_used": False,
                },
            ),
            task_slug=active["slug"],
        )
        validation, request = self._validator_packet(validator)
        if request is None:
            return validation
        clarification = self.harness.invoke(
            "worker",
            self._prompt(
                "worker",
                {
                    "task": active,
                    "goal": state["goal"],
                    "clarification": request,
                },
            ),
            task_slug=active["slug"],
            follow_up=True,
        )
        clarified_do = self._merge_do(do, self._worker_packet(clarification))
        follow_up = self.harness.invoke(
            "validator",
            self._prompt(
                "validator",
                {
                    "task": active,
                    "goal": state["goal"],
                    "worker_packet": {"do": clarified_do},
                    "clarification_already_used": True,
                },
            ),
            task_slug=active["slug"],
            follow_up=True,
        )
        validation, repeated_request = self._validator_packet(follow_up)
        if repeated_request is not None:
            raise TransitionError(
                "validator requested more than one clarification"
            )
        do.clear()
        do.update(clarified_do)
        return validation

    def _assessor_clarifications(
        self,
        state: dict[str, Any],
        active: dict[str, Any],
        packet: dict[str, Any],
        requests: list[dict[str, str]],
    ) -> list[dict[str, Any]]:
        replies: list[dict[str, Any]] = []
        for item in requests:
            target, request = item["target"], item["request"]
            response = self.harness.invoke(
                target,
                self._prompt(
                    target,
                    {
                        "task": active,
                        "goal": state["goal"],
                        "completed_packet": packet,
                        "assessor_clarification": request,
                    },
                ),
                task_slug=active["slug"],
                follow_up=True,
            )
            if target == "worker":
                evidence = self._worker_packet(response)
            else:
                validation, repeated_request = self._validator_packet(response)
                if repeated_request is not None:
                    raise TransitionError(
                        "validator cannot request clarification during assessor clarification"
                    )
                evidence = validation
            replies.append(
                {"target": target, "request": request, "response": evidence}
            )
        return replies

    @staticmethod
    def _worker_packet(worker: Any) -> dict[str, Any]:
        if not isinstance(worker, dict) or not isinstance(
            worker.get("do"), dict
        ):
            raise StateError("worker response must contain do")
        do = cast(dict[str, Any], deepcopy(worker["do"]))
        if not isinstance(do.get("summary"), str) or not do["summary"].strip():
            raise StateError("worker.do.summary is required")
        if not isinstance(do.get("evidence"), list) or not all(
            isinstance(item, str) and item.strip() for item in do["evidence"]
        ):
            raise StateError(
                "worker.do.evidence must be a list of non-empty strings"
            )
        return do

    @staticmethod
    def _validator_packet(validator: Any) -> tuple[dict[str, Any], str | None]:
        if not isinstance(validator, dict) or not isinstance(
            validator.get("validate"), dict
        ):
            raise StateError("validator response must contain validate")
        validation = cast(dict[str, Any], deepcopy(validator["validate"]))
        request = validator.get("clarification_request")
        packet = {
            "slug": "packet",
            "intent": "packet",
            "criteria": ["packet"],
            "do": {"summary": "packet", "evidence": []},
            "validate": validation,
        }
        validate_task(packet, "validator response", True)
        if request is not None and (
            not isinstance(request, str) or not request.strip()
        ):
            raise StateError(
                "validator.clarification_request must be a non-empty string or null"
            )
        return validation, request

    @staticmethod
    def _merge_do(
        original: dict[str, Any], clarification: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "summary": original["summary"],
            "evidence": _dedupe(
                [*original["evidence"], *clarification["evidence"]]
            ),
        }

    @staticmethod
    def _completed_packet(
        active: dict[str, Any], do: dict[str, Any], validation: dict[str, Any]
    ) -> dict[str, Any]:
        return validate_task(
            {
                **deepcopy(active),
                "do": deepcopy(do),
                "validate": deepcopy(validation),
            },
            "completed packet",
            True,
        )

    def _assess(
        self,
        state: dict[str, Any],
        active: dict[str, Any],
        packet: dict[str, Any],
        *,
        clarification_used: bool,
        clarifications: list[dict[str, Any]],
    ) -> dict[str, Any]:
        assessor = self.harness.invoke(
            "assessor",
            self._prompt(
                "assessor",
                {
                    "goal": state["goal"],
                    "lessons": state["lessons"],
                    "task": active,
                    "worker_packet": {"do": packet["do"]},
                    "validator_packet": {"validate": packet["validate"]},
                    "clarifications": clarifications,
                    "clarification_already_used": clarification_used,
                },
            ),
            task_slug=active["slug"],
            follow_up=clarification_used,
        )
        if not isinstance(assessor, dict) or not isinstance(
            assessor.get("retro"), dict
        ):
            raise TransitionError("assessor returned an incomplete response")
        retro = assessor["retro"]
        if any(
            not isinstance(retro.get(k), list)
            or not all(
                isinstance(item, str) and item.strip() for item in retro[k]
            )
            for k in ("wins", "issues", "actions")
        ):
            raise TransitionError("assessor retro is invalid")
        requests = assessor.get("clarification_requests")
        if not isinstance(requests, list):
            raise TransitionError("assessor clarification requests are invalid")
        if clarification_used and requests:
            raise TransitionError(
                "assessor requested more than one clarification round"
            )
        return {
            "retro": deepcopy(retro),
            "clarification_requests": deepcopy(requests),
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

    def _prompt(self, role: str, context: dict[str, Any]) -> str:
        return build_prompt(role, context, self.change_path)
