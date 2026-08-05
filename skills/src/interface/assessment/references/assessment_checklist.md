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
