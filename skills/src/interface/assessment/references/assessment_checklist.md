# Assessment Contract Checklist

Use this for conformance checks. An assessment contract passes when every critical item passes.

## Critical

- [ ] The assessment has `In Scope` and `Out of Scope` resource lists.
- [ ] Each question addresses one or more in-scope resource groups.
- [ ] Each question has a unique `Q-<CATEGORY>-<three-digit sequence>` ID and short title.
- [ ] Every question uses exactly the required flat fields: Question, Answer, Status, Evidence found, Impact, Confidence, and Follow-up.
- [ ] Every status is Pass, Partial, Fail, or Insufficient evidence.
- [ ] Every impact and confidence value is High, Medium, or Low.
- [ ] Every Pass, Partial, or Fail answer cites one or more permitted evidence references; `None` is not allowed.
- [ ] Insufficient-evidence answers explicitly identify the missing or limited evidence and may use `None` for `Evidence found`.
- [ ] The summary groups question IDs by all four statuses and identifies the next follow-up.
- [ ] The assessment has no required lenses, role-based phrasing, blocking classification, separate target field, or completion goal.

## Optional but Checkable

- [ ] Every category is relevant to the declared scope.
- [ ] Every category heading uses the canonical Title Case name and prefix.
- [ ] Follow-ups are concrete when the status is Partial, Fail, or Insufficient evidence.
- [ ] The assessment uses `assessment` for the complete artifact and `question` for an individual evaluation unit.

## Quality

A failed Quality item produces a `Partial` result. It does not fail conformance.

- [ ] The in-scope and out-of-scope resource lists define clear evaluation boundaries.
- [ ] Each question identifies the in-scope resource group it evaluates.
- [ ] Selected categories are relevant to the declared scope, with no material relevant category omitted.
- [ ] Each question invites a specific, grounded answer rather than a vague or purely binary response.
- [ ] Pass, Partial, and Fail answers cite permitted evidence references rather than `None`, while Insufficient evidence answers explicitly identify missing evidence.
- [ ] Statuses are consistent with the answer and evidence.
- [ ] Impact and confidence are calibrated to the consequence and strength of evidence.
- [ ] Follow-ups are concrete and useful for Partial, Fail, and Insufficient evidence answers.
- [ ] The status-grouped summary is accurate and its next follow-up prioritizes the highest-value unresolved work.
- [ ] The assessment is concise and free of lenses, role framing, stop conditions, and completion-goal logic.
