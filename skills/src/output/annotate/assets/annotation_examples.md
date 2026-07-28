# Annotation Examples

Concrete examples of each annotation kind across file types.

## NOTE — Knowledge

### TypeScript

```ts
// NOTE(AUTH-ARCH-1): Service mesh uses sidecar pattern for all inter-service communication
// refs: [arch/decisions/ADR-004.md]
const mesh = new SidecarMesh();
```

### Python

```python
# NOTE(AUTH-ARCH-2): Database connections use connection pooling with max 50 connections
# refs: [config/db.py:22, SPEC-SYS.md#QUA-CON-1]
DB_POOL_SIZE = 50
```

### Markdown

```markdown
<!-- NOTE(AUTH-ARCH-3): All API responses include X-Request-ID header for tracing -->
<!-- refs: [arch/decisions/ADR-010.md] -->

## API Design

...
```

## TODO — Action Item

### TypeScript

```ts
// TODO(AUTH-ARCH-4): Implement retry logic with exponential backoff for failed mesh calls
// refs: [src/mesh/client.ts:89, RFC-SYS#RESILIENCE-2]
async function callService(name: string): Promise<Response> { ... }
```

### YAML

```yaml
# TODO(AUTH-ARCH-5): Add circuit breaker configuration for downstream services
# refs: [deploy/k8s/deployment.yaml:45, RFC-SYS#RESILIENCE-3]
services:
  mesh: enabled
```

### SQL

```sql
-- TODO(AUTH-ARCH-6): Add unique constraint on (user_id, service_name) to prevent duplicate registrations
-- refs: [db/migrations/005_create_registrations.sql:12, SPEC-SYS.md#FUT-3]
CREATE TABLE registrations (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    service_name TEXT NOT NULL
);
```

## CHECK — Verification

### TypeScript

```ts
// CHECK(AUTH-ARCH-7): Verify retry backoff does not exceed 30s max delay
// refs: [tests/mesh/retry.test.ts, RFC-SYS#RESILIENCE-2]
function retryWithBackoff(fn: Function): Promise<any> { ... }
```

### Python

```python
# CHECK(AUTH-ARCH-8): Verify connection pool does not exceed 50 connections under load test
# refs: [tests/db/pool_test.py, config/db.py:22]
def test_pool_limits():
    ...
```

### Markdown

```markdown
<!-- CHECK(AUTH-ARCH-9): Verify X-Request-ID is present in all API responses including errors -->
<!-- refs: [tests/api/tracing.test.ts, arch/decisions/ADR-010.md] -->

## Tracing

...
```

## REVIEW — Comparison

### TypeScript

```ts
// REVIEW(AUTH-ARCH-10): Implementation uses synchronous connection pool but RFC-SYS#PERF-4 recommends async initialization
// refs: [src/db/pool.ts:34, RFC-SYS.md#PERF-4]
class ConnectionPool { ... }
```

### Markdown

```markdown
<!-- REVIEW(AUTH-ARCH-11): ADR-004 sidecar pattern conflicts with cost constraint in SPEC-SYS#QUA-CON-1 -->
<!-- refs: [arch/decisions/ADR-004.md, SPEC-SYS.md#QUA-CON-1] -->

## Architecture Decisions

...
```

### YAML

```yaml
# REVIEW(AUTH-ARCH-12): Circuit breaker config uses fixed threshold but RFC-SYS#RESILIENCE-5 recommends adaptive thresholds
# refs: [deploy/k8s/deployment.yaml:50, RFC-SYS.md#RESILIENCE-5]
circuit_breaker:
  threshold: 100
```

## DONE — Completion

### TypeScript

```ts
// DONE(AUTH-ARCH-4): Retry logic with exponential backoff implemented per RFC-SYS#RESILIENCE-2
// refs: [src/mesh/client.ts:89, RFC-SYS.md#RESILIENCE-2]
async function callService(name: string): Promise<Response> { ... }
```

### Python

```python
# DONE(AUTH-ARCH-5): Circuit breaker added with adaptive thresholds per RFC-SYS#RESILIENCE-5
# refs: [deploy/k8s/deployment.yaml:50, RFC-SYS.md#RESILIENCE-5]
circuit_breaker:
  threshold: adaptive
```

### Markdown

```markdown
<!-- DONE(AUTH-ARCH-11): ADR-004 updated to include cost-optimized sidecar option -->
<!-- refs: [arch/decisions/ADR-004.md, SPEC-SYS.md#QUA-CON-1] -->

## Architecture Decisions

...
```

## refs: — Reference Patterns

### Single reference

```ts
// TODO(AUTH-ARCH-13): Add logging for mesh connection events
// refs: [src/mesh/client.ts:100]
```

### Multiple references

```ts
// REVIEW(AUTH-ARCH-14): Connection pool size may need tuning based on load test results
// refs: [config/db.py:22, tests/db/load_test.py, SPEC-SYS.md#QUA-CON-1]
```

### Mixed reference types

```ts
// TODO(AUTH-ARCH-15): Document connection pool configuration for ops team
// refs: [config/db.py:22, https://docs.example.com/ops/pool-config#monitoring, SPEC-SYS.md#EXP-2]
```

### Reference with anchor

```ts
// CHECK(AUTH-ARCH-16): Verify pool metrics are exported to monitoring
// refs: [config/db.py#metrics-section, RFC-SYS.md#METRICS-1]
```
