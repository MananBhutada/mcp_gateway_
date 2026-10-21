# System design

## Data model

The gateway models users, API keys, upstream MCP servers, tool permissions, audit records and invitation tokens. PostgreSQL is the intended persistent control-plane database. Raw user API keys are shown once; stored key material is hashed. Upstream credentials should be encrypted at rest where persisted and injected from runtime secrets.

## Control plane and data plane

- **Control plane:** server registry, enabled/health state, user/key lifecycle, roles, tool permissions and audit access.
- **Data plane:** MCP authentication, namespaced tool discovery, authorization, upstream invocation, timeout handling and response/audit generation.
- **Dashboard:** consumes the gateway API and same-origin MCP proxy; it is not an authorization substitute.

## Design trade-offs

- Synchronous SQLAlchemy operations keep the assignment implementation straightforward; higher load may justify async database access.
- In-memory tool/health caches are simple but not a shared coordination mechanism. Multi-replica production deployment should use shared cache/pub-sub or database-backed refresh coordination.
- Stateless JSON-RPC/HTTP handling is simpler than long-lived streaming sessions; confirm compatibility with the actual MCP client versions used in the demo.
- Tool results are untrusted input. Chat must not treat returned text as instructions, and destructive operations should require appropriate confirmation.
- A PVC protects against pod replacement but is not a backup or disaster-recovery strategy.

## Scaling and reliability follow-ups

For a production system, add rate limits, concurrency controls, circuit breakers, shared cache invalidation, schema migrations, structured metrics/tracing, backups/restore drills, key rotation/expiry policy, and deployment rollback procedures. These are explicit follow-ups, not claims that the assignment already includes them.
