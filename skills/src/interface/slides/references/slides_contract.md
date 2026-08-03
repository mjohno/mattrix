# Executive Slides Contract

The default `slides` profile is `executive-decision`: a markdown deck that gives an executive audience enough context to make a named decision. The secondary `executive-status` profile is a single-slide progress update.

## Shared Markdown Rules

- Start with one `#` title; add a short subtitle only when useful.
- Separate slides with a line containing only `---`.
- Start each non-title slide with one `##` takeaway heading.
- Make each heading state the conclusion, status, decision, or ask—not only its topic.
- Use short, parallel phrases. A bullet has at most six key words and a slide has at most six bullets.
- Use `-` lists only when they improve scanning; do not nest them.
- Use Markdown links for supporting cloud documents: `[label](https://...)`.
- When supporting context exists, place a direct cloud link on the relevant slide. Link to the full source, not a link index.
- Embed only the excerpt needed to understand the takeaway; keep the complete background material in its linked cloud document.

## Executive-Decision Profile

Use this profile by default. Its decision pathway is:

1. Decision requested
2. Why the decision matters now
3. Essential evidence, options, or trade-offs
4. Recommendation
5. Owner and next step

A deck may combine adjacent pathway elements when the decision remains clear. Every evidence or reference slide must include its direct cloud link when supporting material exists.

## Executive-Status Profile

Use this profile only for a status update. It contains exactly one slide, after an optional title line, and must include:

- Overall status or takeaway
- Essential progress highlights
- Material risk, blocker, or decision needed
- Next milestone or owner
- Direct cloud links to underlying details when they exist

Use compact labeled sections or a simple table to keep the single slide scannable. Do not add a second content, appendix, or references slide.

## Project-Roadmap-Update Profile

Use this profile for executive alignment on delivery sequencing and strategic outcomes. Its update pathway is:

1. Overall roadmap health and strategic outcome
2. Completed or changed milestones
3. Upcoming milestones and material dependencies
4. Risk, trade-off, or escalation
5. Decision needed or explicit confirmation that none is needed

Show only milestones that change executive confidence, priority, or a decision. Link each supporting roadmap, plan, or metric to its full cloud source when it exists.

## Visionary-Story Profile

Use this profile to build commitment to a future direction. Its narrative pathway is:

1. Current reality
2. Strategic tension
3. Envisioned future
4. Credible path
5. Commitment, decision, or next step requested

State the future-state thesis early. Make the current-to-future gap concrete, include only evidence that strengthens the narrative, and link its full cloud source when it exists.

## Technical-Review Profile

Use this profile for technical teams, engineers, and implementation leads who need implementation and maintenance context. Its review pathway is:

1. Technical decision or review objective
2. System architecture, schema, code excerpt, or diagram
3. Dependencies and implementation pathway
4. Trade-offs, edge cases, and known risks
5. Recommended decision, owner, or follow-up

Prefer precise code snippets, schema excerpts, and diagrams over abstract summaries. Every technical excerpt must be necessary, labeled, and linked to its full cloud source when one exists.

## Educational Profile

Use this profile for learners, team members, or stakeholders adopting a concept, behavior, process, or framework. Its teaching pathway is:

1. Learning objective
2. Foundational concept
3. Guided example or scenario
4. Application of the concept
5. Key takeaway and behavioral action

Each slide has one clear learning objective or supports the current objective. Introduce foundations before complex application, and use concrete examples to make the expected behavior actionable.

## Layered-Briefing Profile

Use this profile for cross-functional stakeholders aligning on direction, strategy, or high-level status. Its briefing pathway is:

1. Headline summary and shared outcome
2. Strategic direction or current alignment
3. Alignment milestones
4. Supporting context for the headline
5. Shared next step or confirmation

Start every slide with its top-level takeaway. Organize detail beneath that takeaway so readers can scan the strategic message first and drill into supporting context only as needed. Exclude implementation detail that does not change shared direction, milestones, or outcomes.

## Optional Overlays

Alternative audiences, objectives, and specialized frameworks beyond these seven profiles are optional overlays selected by the calling skill. They may add rules, but do not require metadata or alter the executive defaults unless explicitly selected.

## Minimal Example

```markdown
# Release Decision

---

## Approve Friday production release

- Decision owner: VP Engineering
- Decision needed: Thursday noon

---

## Readiness evidence supports approval

- Critical tests passed
- Security review completed
- Rollback rehearsal succeeded
- [Full readiness evidence](https://cloud.example.com/release-readiness)

---

## Deploy after approval

- Owner: Release Manager
- Next step: schedule deployment window
```
