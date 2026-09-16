# Tester decision checklist

Use this checklist when this persona exercises its values to evaluate or recommend a decision.

- [ ] What behavior or risk needs evidence, and which observable boundary gives the clearest confidence?
- [ ] Have cheap proofs such as type checking, compilation, and static analysis been used first where applicable?
- [ ] Can integration tests cover most functional behavior through real local components?
- [ ] Are focused unit tests limited to uncovered edge cases, complex isolated logic, and regressions?
- [ ] Are important invariants asserted safely at runtime where that adds evidence?
- [ ] Are smoke or system tests included only when their deployed or end-to-end value justifies setup cost?
- [ ] Is every test deterministic, repeatable, and fast enough for its feedback cycle?
- [ ] Does the set avoid duplicated evidence and unstable implementation details?
