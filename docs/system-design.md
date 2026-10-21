# System design

## Data model
The gateway models users, API keys, upstream MCP servers, tool permissions, audit events and invitation tokens. PostgreSQL is the persistent control-plane database. Raw user API keys are shown once; stored key material is hashed. Upstream credentials should be encrypted at rest where persisted and supplied at runtime through Kubernetes Secrets.

## Control plane and data plane
- **Control plane:** registry, enabled/health state, user/key lifecycle, role/tool permissions and audit access.
- **Data plane:** MCP authentication, namespaced discovery, authorization, upstream invocation, timeout handling and audit/result generation.
- **Dashboard:** calls gateway APIs and its same-origin MCP proxy; UI visibility is not an authorization boundary.

## Trade-offs
- Synchronous SQLAlchemy operations simplify the assignment but may need async DB access at higher load.
- Per-replica in-memory tool/health caches are simple but do not coordinate across replicas; production scaling may require shared cache/pub-sub or database-backed refresh coordination.
- Stateless HTTP handling is simpler than long-lived streaming; compatibility must be tested with the actual MCP client.
- Tool output is untrusted input. Chat must not treat it as instructions; destructive actions may require confirmation.
- PVCs preserve data across pod replacement but are not backups.

## Production follow-ups
Rate limits, concurrency controls, circuit breakers, shared cache invalidation, schema migrations, metrics/tracing, backup/restore drills, key rotation/expiry and deployment rollback procedures should be addressed before production use. These are follow-ups, not claims that this assignment already includes them.
