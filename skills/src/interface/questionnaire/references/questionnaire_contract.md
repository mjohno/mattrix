# How to Define a Good Questionnaire Contract

The canonical layout is the [template](assets/questionnaire_template.md).

Use this reference for design rules and contract rules.

## Question Design Rules

- Each question probes a specific judgment area derived from spec requirements + persona criteria.
- Avoid binary phrasing. Favor questions that invite nuanced analysis (how, why, to what extent, what trade-offs, under what conditions).
- Include at least one question per persona lens.
- Prioritize: P1-equivalent areas first (structural/spec violations), then P2/P3 (quality/clarity).
- Base criteria (consistency, clarity) should appear as early questions when the artifact's quality is a review target.
- Each question should map to at least one spec requirement or persona criterion.

## Contract Rules

- Questions are **evaluable by an LLM** — they ask for reasoning anchored in the artifact content + loaded criteria, not external research.
- The number of questions should be bounded (aim for 8–15) to keep execution tractable.
- If a persona adds no meaningful perspective beyond another already-loaded lens, do not create a separate section.
- Source criteria mapping is required: every question must trace back to at least one spec ID or persona criterion so findings can cite sources.
