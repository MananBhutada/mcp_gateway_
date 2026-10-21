# System design

## Data model

The gateway models users, API keys, upstream MCP servers, tool permissions, audit events, and invitation tokens. PostgreSQL is the persistent control-plane database. Raw user API keys are shown once; stored key material is hashed. Upstream credentials registered through the gateway are encrypted before being stored in the database. Deployment credentials are supplied through Kubernetes Secret references; Kubernetes Secret encryption at rest depends on cluster configuration.

## Control plane and data plane

- **Control plane:** registry, enabled/health state, user/key lifecycle, role/tool permissions, and audit access.
- **Data plane:** MCP authentication, namespaced discovery, authorization, upstream invocation, timeout handling, and audit/result generation.
- **Dashboard:** calls gateway APIs and its same-origin MCP proxy; UI visibility is not an authorization boundary.

## Architecture choices and trade-offs

- **FastAPI gateway as MCP client and server.** The gateway exposes one authenticated `/mcp` endpoint to clients and acts as an MCP client to each registered upstream. This centralizes authentication, tool discovery, permission enforcement, routing, timeout handling, and audit events. All tool calls pass through this trust boundary.
- **WooCommerce REST rather than WP-CLI or direct SQL.** `services/woo-mcp/app/woocommerce.py` sends requests to the WooCommerce REST API and signs them with the configured WooCommerce consumer key/secret. This uses WooCommerce's supported commerce API and business logic instead of bypassing it through database writes or shell commands.
- **One Helm chart with environment values.** `infrastructure/helm/urumi` defines shared workloads and policies; `values-local.yaml` and `values-prod.yaml` supply environment-specific hosts, TLS secret, storage, image tags, replica counts, and secrets. Production uses the same chart templates as local deployment, with production-specific values and deploy-time secrets.
- **PostgreSQL for the control plane.** The chart provisions PostgreSQL and a PVC. The gateway models users, key hashes, server registry, permissions, invitations, and audit logs in SQLAlchemy. The store uses a separate MySQL database for WordPress/WooCommerce.
- **Streamable HTTP.** `services/gateway/app/mcp/server.py` implements MCP JSON-RPC over HTTP at `/mcp` and describes the endpoint as stateless Streamable HTTP. Each request authenticates its bearer token; the upstream client opens a short-lived Streamable HTTP session for each list/call. This avoids gateway-side long-lived session affinity but requires clients to support the implemented protocol behavior.

## Tool aggregation, routing, and failure handling

1. The health loop calls `refresh_all()` every `HEALTH_INTERVAL` seconds (default 15, configured by `HEALTH_INTERVAL` in `services/gateway/app/config.py`). Each enabled server is checked with an MCP `list_tools` request using `UPSTREAM_TIMEOUT` (default 5 seconds).
2. Healthy upstream tool definitions are cached per gateway process. `tools_for(user)` combines those tools and filters them through role/tool permissions. Names use `<server>__<tool>`; for example, WooCommerce `list_products` is exposed as `woocommerce__list_products`.
3. On `tools/call`, the gateway splits the namespace, confirms that the server exists and is enabled, checks the user's permission again, revalidates the stored URL, decrypts that server's credential, and invokes the tool with `UPSTREAM_CALL_TIMEOUT` (default 30 seconds).
4. The upstream MCP client in `services/gateway/app/mcp/client.py` applies a timeout to each short-lived connection/session and call. A refresh exception removes that server's cached tools and records its status as `unreachable`; `refresh_all()` isolates refresh failures across servers. Failure isolation was demonstrated in the recorded local k3d run.
5. `R.execute` writes an audit event for successful tool results and error/exception paths. The record includes user, server, tool, source (`mcp` or `chat`), start time, duration, success, and error. Audit attribution was demonstrated in the recorded local k3d run.

The in-memory `TOOL_CACHE` is per process, not shared between gateway replicas. Each replica runs its own health loop and can temporarily have a different view of upstream availability or tools.

## Production configuration differences

The table lists differences visible between `values-local.yaml` and `values-prod.yaml`. Shared values inherited from `values.yaml` are not repeated as differences.

| Setting | Local values | Production values | Operational consequence |
|---|---|---|---|
| Environment | `development` | `production` | Production config validation is enabled. |
| Ingress hosts | `store.urumi.local`, `dashboard.urumi.local` | `store.YOURDOMAIN.com`, `app.YOURDOMAIN.com` placeholders | Replace placeholders and point DNS A records to the VPS public IP. |
| Ingress class | `traefik` | Inherits `traefik` from shared defaults | The VPS needs the matching Ingress controller. |
| TLS | No `tlsSecret` in local values | `urumi-tls` | Production values reference a TLS Secret but do not create it or install cert-manager. |
| WordPress scheme | Shared default `http` | `https` | TLS termination and forwarded-proto behavior must match the deployed ingress. |
| LLM URL/model | OpenRouter `https://openrouter.ai/api/v1`, `openrouter/free` | Same | The provider key remains a Secret value; local values leave it empty. |
| Storage class and sizes | No explicit class; MySQL 2Gi, WordPress 2Gi, PostgreSQL 1Gi | `local-path`; MySQL 10Gi, WordPress 10Gi, PostgreSQL 5Gi | The cluster needs a suitable provisioner and adequate disk capacity. |
| Replica counts | Shared defaults: gateway 1, dashboard 1, MCP 1 | Gateway 2, dashboard 2, MCP 1 | Two gateway replicas have independent in-memory tool caches. |
| Image references | `urumi/*:latest` | `ghcr.io/YOURUSER/urumi-*:0.1.0` placeholders | Build, push, and configure real registry paths/tags before deployment. |
| Pull policy | `IfNotPresent` | `Always` | Production nodes pull the configured image tag. |
| Resources | Shared `resources.small` / `resources.db` values | No override in `values-prod.yaml` | Production values do not define separate production resource limits. |

**TLS status:** the chart renders Ingress TLS only when `ingress.tlsSecret` is non-empty. The production values name `urumi-tls`, but the supplied files do not create that Secret, configure cert-manager, or issue a certificate. TLS is a deployment prerequisite.

## Scaling note

The gateway MCP endpoint authenticates each HTTP request independently and does not store MCP sessions in a shared session store. The Helm production values set two gateway replicas. However, `TOOL_CACHE` in `services/gateway/app/routing/router.py` is process-local, and each replica runs its own health loop. There is no shared cache or invalidation mechanism, so replica state can temporarily differ.

## Upgrade and rollback with Helm

Run from the repository root and choose the values file for the target environment. Supply unique production secrets through deployment-time overrides or an approved secret manager; do not commit secret values.

Local update:

```powershell
helm upgrade --install urumi infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
helm history urumi
# Replace <REVISION> with the revision to restore:
helm rollback urumi <REVISION>
```

Production update (replace placeholders and provide the required secret overrides):

```powershell
helm upgrade --install urumi infrastructure/helm/urumi -f infrastructure/helm/urumi/values-prod.yaml
helm history urumi
# Replace <REVISION> with the revision to restore:
helm rollback urumi <REVISION>
```

A Helm rollback restores a prior release revision. Check pods, Jobs, PVCs, Ingress, application behavior, and database compatibility after rollback. Do not delete PVCs as a rollback shortcut.

## Trade-offs and known limitations

- Synchronous SQLAlchemy operations simplify the assignment but can require async DB access at higher load.
- Per-replica in-memory tool/health caches do not coordinate across replicas; production scaling can require shared cache/pub-sub or database-backed refresh coordination.
- PVCs preserve data across pod replacement but are not backups.
- The chart does not install cert-manager, configure Kubernetes Secret encryption at rest, or implement HTTP-level rate limits.
- The SSRF validator does not block loopback IP literals. Private and cluster IPs are allowed for in-cluster MCP endpoints.
