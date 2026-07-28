# Questionnaire Quality Criteria

Use this for evaluating a questionnaire contract's quality. Quality is about coverage, traceability, and evaluability by an LLM.

## Review Questions

1. Does each question probe something specific that can be evaluated against the loaded artifact content?
2. Are questions phrased to invite nuanced analysis rather than binary answers?
3. Is the priority ordering defensible — do the most impactful questions come first?
4. Does every question map to at least one spec ID or persona criterion in the Source Criteria section?
5. Are there gaps where a spec requirement or persona lens has no corresponding question?
6. Is the base criteria treatment appropriate — are consistency/clarity questions included when relevant?
7. Would an LLM executing this review have enough context to answer each question without external research?
8. Do overlapping or redundant questions exist that could be consolidated?
9. Are role descriptions in the Lenses section sufficient to frame questions correctly during execution?

## Common Findings

- Too few questions, leaving spec requirements or questionnaire lenses unexamined.
- Binary phrasing that reduces nuance (e.g., "Does this implement X?" instead of "How does X handle edge case Y under Z condition?").
- Questions with no traceable source — invented criteria rather than derived from specs/personas.
- Role descriptions missing or vague, making lens framing inconsistent across execution.
