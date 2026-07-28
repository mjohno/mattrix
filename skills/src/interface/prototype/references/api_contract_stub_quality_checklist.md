# API Contract Stub Quality Checklist

Use this checklist when outlining, drafting, modifying, or reviewing an API contract stub prototype.

## Critical
- [ ] States the decision the contract stub will inform.
- [ ] Names the integration, consumer/provider, or semantic assumption being tested.
- [ ] Identifies consumers, providers, and environment expectations.
- [ ] Defines endpoint path, method, purpose, and version/base URL assumptions.
- [ ] Includes request shape with required fields and example values.
- [ ] Includes success response shape with example values.
- [ ] Includes relevant error responses and status codes.
- [ ] Notes auth, idempotency, pagination, rate limits, or async behavior if relevant.
- [ ] Defines validation signals, such as consumers confirming they can build against the stub.
- [ ] Defines failure signals, such as missing field semantics or incompatible lifecycle assumptions.
- [ ] Lists omitted production concerns.

## Quality
- [ ] Uses a standard machine-readable shape when practical, such as OpenAPI YAML.
- [ ] Keeps examples realistic but fake.
- [ ] Documents field meaning, not just field names.
- [ ] Avoids premature completeness beyond the integration decision.
- [ ] Ends with a clear next decision.
