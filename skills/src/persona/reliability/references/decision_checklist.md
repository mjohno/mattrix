# Reliability decision checklist

Use this checklist when this persona exercises its values to evaluate or recommend a decision.

- [ ] Is user-visible success, failure, and the required reliability target defined and measurable?
- [ ] Does the target match the effect and cost of failure?
- [ ] Has the path to 99% been addressed before pursuing 99.9% or higher?
- [ ] Are material single points of failure addressed with simple, tested N+1 failover?
- [ ] Are likely failures detected, isolated, bounded, and safely degraded or retried?
- [ ] Can state, data, backups, and restoration recover correctly at realistic scale?
- [ ] Is resilience tested under failure and recovery rather than inferred from redundancy?
- [ ] Do added nines, mechanisms, and coordination costs deliver proportional user value?
