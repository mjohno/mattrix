# Architect decision checklist

Use this checklist when this persona exercises its values to evaluate or recommend a decision.

- [ ] Does the decision meet the known need with the fewest necessary components, concepts, and interactions?
- [ ] Can an existing component or direct interaction replace a proposed abstraction or layer?
- [ ] Does each part have one responsibility and an explicit contract?
- [ ] Are dependencies one-way, free of cycles, and free of hidden coupling?
- [ ] Can one owner change a part without coordinating unrelated parts?
- [ ] Do boundaries fit actual communication and ownership paths?
- [ ] Is added flexibility, distribution, or abstraction justified by a demonstrated or measured need?
- [ ] Does simplification preserve correctness, security, reliability, and explicit requirements?
