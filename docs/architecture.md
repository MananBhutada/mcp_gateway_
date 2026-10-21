# Architecture — Urumi MCP Gateway

## Components

- **Dashboard:** React/TypeScript UI for gateway access, registry and administrative workflows; the same-origin proxy forwards API and MCP requests to the gateway.
- **Gateway:** FastAPI control/data plane. Authenticates caller keys, applies role and tool permissions, lists namespaced tools, routes calls to upstream MCP servers, and records audit events.
- **WooCommerce MCP:** exposes product/order tools and uses WooCommerce REST API credentials injected at runtime.
- **Weather MCP and Currency MCP:** independent upstreams demonstrating multi-server aggregation and isolation.
- **Storefront:** WordPress with WooCommerce, backed by MySQL and persistent volumes.
- **Gateway state:** PostgreSQL holds users, API-key metadata, server registry, permissions, invitations and audit records.
- **Kubernetes/Helm:** deploys services, internal Services, Ingress, Secrets, PVCs, probes, resource controls and NetworkPolicies.

## Request flow

1. MCP client sends a request to the gateway `/mcp` endpoint with a per-user bearer key.
2. Gateway authenticates the key and resolves the caller/role.
3. `tools/list` combines tools from enabled/healthy upstreams, prefixes names with the upstream identifier, and applies caller permissions.
4. `tools/call` validates the requested tool, checks permission again at execution time, invokes the relevant upstream with a timeout, and records the result.
5. The gateway returns a safe result/error. Upstream secrets are not returned to the client or model.

## Trust boundaries

- Public-facing entry points should be limited to the dashboard and storefront Ingress.
- WooCommerce MCP, Weather MCP, Currency MCP, MySQL and PostgreSQL should remain internal.
- Commerce data is accessed through WooCommerce REST, not direct gateway-to-MySQL queries.
- Runtime credentials are sourced from Kubernetes Secrets, not committed source files.
- NetworkPolicies restrict traffic to the required callers; rendered and live policy behavior must be verified.

## Invariants

- All tool calls from chat and external MCP clients pass through gateway authorization and audit.
- Server/tool names are collision-safe.
- Disabling an upstream removes its tools from discovery and rejects stale calls.
- One unhealthy upstream must not prevent healthy upstreams from being called.
- MySQL and PostgreSQL have separate credentials and persistent claims.
- PVCs are persistence, not backup; a backup/restore plan is still needed for real production use.

## Deployment environments

Use the same chart with `values-local.yaml` for local k3d and `values-prod.yaml` for a production-like k3s/VPS environment. Production additionally requires TLS, unique secrets, restricted ingress/egress, operational backups, and monitoring. The architecture is the intended design; acceptance evidence is tracked in `STATUS.md` and `live-acceptance-tests.md`.
