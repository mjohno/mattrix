from __future__ import annotations

from typing import Any

from .state import is_completed


def _list(lines: list[str], label: str, values: Any) -> None:
    if not isinstance(values, list) or not values:
        return
    lines.extend([f"**{label}:**", *[f"- {value}" for value in values], ""])


def _task(lines: list[str], task: dict[str, Any], recommended: bool) -> None:
    lines.extend([f"### {task['slug']}", ""])
    if recommended:
        lines.extend(["**RECOMMENDED**", ""])
    lines.extend([f"**Intent:** {task['intent']}", ""])
    _list(lines, "Criteria", task["criteria"])


def render_gate(gate: dict[str, Any]) -> str:
    """Render a validated STEP gate as the owner-facing Markdown review."""
    # NOTE(MDFORMAT-1): Gate text is intentionally rendered as visual Markdown.
    # It is not escaped because this output is not a control or storage format.
    current = gate.get("current")
    proposals = gate["proposals"]
    recommended = gate["recommended"]
    terminal_signoff = (
        isinstance(current, dict)
        and is_completed(current)
        and not proposals
        and recommended == "terminate"
    )
    title = current["slug"] if isinstance(current, dict) else "Initial Plan"
    lines = [f"# STEP Review - {title}", "", f"**Goal:** {gate['goal']}", ""]
    _list(lines, "Lessons", gate["lessons"])

    if isinstance(current, dict):
        lines.extend([f"**Intent:** {current['intent']}", ""])
        _list(lines, "Acceptance Criteria", current["criteria"])
        execution = current.get("do")
        if isinstance(execution, dict):
            lines.extend(
                ["## Execution", "", f"**Summary:** {execution['summary']}", ""]
            )
            _list(lines, "Implementation Evidence", execution.get("evidence"))
        validation = current.get("validate")
        if isinstance(validation, dict):
            lines.extend(
                [
                    "## Validation",
                    "",
                    f"**Result:** {validation['result']}",
                    "",
                    f"**Summary:** {validation['summary']}",
                    "",
                ]
            )
            _list(lines, "Evidence", validation.get("evidence"))
        retro = current.get("retro")
        if isinstance(retro, dict) and any(
            retro.get(key) for key in ("wins", "issues", "actions")
        ):
            lines.extend(["## Retro", ""])
            _list(lines, "Wins", retro.get("wins"))
            _list(lines, "Issues", retro.get("issues"))
            _list(lines, "Actions", retro.get("actions"))

    lines.extend(["## Next Tasks", ""])
    if terminal_signoff:
        lines.extend(["No further tasks proposed.", ""])
    else:
        for task in proposals:
            _task(lines, task, task["slug"] == recommended)

    lines.extend(["## Recommendation", ""])
    if terminal_signoff:
        lines.extend(["No further task. Approve to complete STEP.", ""])
    elif recommended is not None:
        lines.extend([recommended, ""])

    lines.append("**Response:**")
    return "\n".join(lines) + "\n"
