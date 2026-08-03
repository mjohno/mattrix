---
name: slides
description: Use when output or map skills need a lightweight markdown slide-deck contract for executive, technical, educational, or cross-functional communication.
metadata:
  type: interface
  category: interface
---

# slides

Goal: Define a lightweight markdown slide-deck contract with executive defaults and optional technical, educational, and cross-functional profiles.
Non-Goals: Do not research, write, render, present, review, or publish a slide deck.
Use-When: Another skill needs the `slides` interface before outlining, drafting, modifying, checking, reviewing, or orchestrating an executive, technical, educational, or layered briefing deck.

## Selection

Default: load only the compact slides contract.

Also select:
- `executive_decision_template.md` when the caller asks to outline or draft an executive decision deck, or does not name a presentation type.
- `executive_status_template.md` when the caller asks to outline or draft an executive status update.
- `project_roadmap_update_template.md` when the caller asks to outline or draft a project roadmap update.
- `visionary_story_template.md` when the caller asks to outline or draft a visionary story.
- `technical_review_template.md` when the caller asks to outline or draft a technical review.
- `educational_template.md` when the caller asks to outline or draft an educational presentation.
- `layered_briefing_template.md` when the caller asks to outline or draft a layered briefing.
- `slides_checklist.md` when the caller asks to check deck conformance.

The default profile is `executive-decision`. These seven presentation types are direct selections; alternative audiences, objectives, and frameworks remain optional overlays supplied by the calling skill. If a requested presentation needs fall outside these profiles, state the unsupported need and hand off to the appropriate skill.

## Context Loading

Load each selected package-local reference or asset into context. Do not paste, quote, summarize, or otherwise reproduce loaded content in chat.

When invoked alone, respond only with `Loaded: <relative path(s)>.` When composed with another task, continue that task without an interface-only response.

Default path:
- `references/slides_contract.md`

Optional paths:
- `assets/executive_decision_template.md`
- `assets/executive_status_template.md`
- `assets/project_roadmap_update_template.md`
- `assets/visionary_story_template.md`
- `assets/technical_review_template.md`
- `assets/educational_template.md`
- `assets/layered_briefing_template.md`
- `references/slides_checklist.md`

## Next Steps

- `outline` — create an executive decision or status skeleton from the selected template.
- `draft` — create a first-pass executive deck using the selected profile.
- `modify` — revise a deck while preserving its decision pathway or status boundary.
- `output/check` — check deck conformance with `slides_checklist.md`.
- `output/review` — review deck quality for its audience and purpose.

## Minimal Example

Prompt: "Use the slides interface to draft an executive release decision deck."
Direct invocation response: `Loaded: references/slides_contract.md.`
