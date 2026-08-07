from stagger_step.render import render_gate


def task(slug: str) -> dict:
    return {"slug": slug, "intent": f"{slug} intent", "criteria": ["done"]}


def test_bootstrap_review_omits_task_sections():
    output = render_gate(
        {
            "goal": "Ship it",
            "lessons": ["Keep scope small"],
            "current": None,
            "proposals": [task("first")],
            "recommended": "first",
            "completed": False,
        }
    )

    assert output.startswith("# STEP Review - Initial Plan\n")
    assert "**Goal:** Ship it" in output
    assert "**Lessons:**\n- Keep scope small" in output
    assert "## Execution" not in output
    assert "## Validation" not in output
    assert "## Retro" not in output
    assert "### first\n\n**RECOMMENDED**" in output
    assert output.endswith("**Response:**\n")


def test_completed_review_renders_task_retro_and_ranked_proposals():
    current = {
        **task("first"),
        "do": {"summary": "Implemented it", "evidence": ["src/file.py"]},
        "validate": {
            "result": "success",
            "summary": "Tests passed",
            "evidence": ["pytest"],
        },
        "retro": {
            "wins": ["Small change"],
            "issues": ["None found"],
            "actions": ["Continue"],
        },
    }
    output = render_gate(
        {
            "goal": "Ship it",
            "lessons": ["Keep scope small"],
            "current": current,
            "proposals": [task("second"), task("third")],
            "recommended": "third",
            "completed": False,
        }
    )

    assert output.startswith("# STEP Review - first\n")
    assert "**Intent:** first intent" in output
    assert "**Acceptance Criteria:**\n- done" in output
    assert "## Execution\n\n**Summary:** Implemented it" in output
    assert "## Validation\n\n**Result:** success" in output
    assert "## Retro\n\n**Wins:**\n- Small change" in output
    assert output.index("### second") < output.index("### third")
    assert output.count("**RECOMMENDED**") == 1
    assert "### third\n\n**RECOMMENDED**" in output
    assert "## Recommendation\n\nthird" in output


def test_incomplete_task_does_not_render_final_signoff_text():
    output = render_gate(
        {
            "goal": "Ship it",
            "lessons": [],
            "current": task("first"),
            "proposals": [],
            "recommended": None,
            "completed": False,
        }
    )

    assert "No further tasks proposed." not in output
    assert "No further task. Approve to complete STEP." not in output


def test_final_signoff_has_terminal_next_task_and_recommendation():
    output = render_gate(
        {
            "goal": "Ship it",
            "lessons": [],
            "current": {
                **task("first"),
                "do": {"summary": "Implemented it", "evidence": []},
                "validate": {
                    "result": "success",
                    "summary": "Tests passed",
                    "evidence": [],
                },
                "retro": {"wins": [], "issues": [], "actions": []},
            },
            "proposals": [],
            "recommended": None,
            "completed": False,
        }
    )

    assert "No further tasks proposed." in output
    assert "No further task. Approve to complete STEP." in output
    assert "## Retro" not in output
    assert output.endswith("**Response:**\n")
