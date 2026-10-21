# Acceptance evidence record

The following requirements were exercised in the recorded local k3d run using `infrastructure/helm/urumi` and `values-local.yaml`. The recording is the evidence artifact.

| Requirement | Implementation (file path) | Verified (recorded local run) | Limitation |
|---|---|---|---|
| Local Helm deployment and workloads | `infrastructure/helm/urumi/Chart.yaml`, `infrastructure/helm/urumi/templates/`, `infrastructure/helm/urumi/values-local.yaml` | Yes | The recorded deployment is local k3d. |
| Storefront product and COD checkout | `infrastructure/helm/urumi/templates/wordpress.yaml`, `infrastructure/helm/urumi/templates/wp-setup.yaml` | Yes | Test customer/order data only. |
| Order visible in WooCommerce admin | `services/woo-mcp/app/woocommerce.py`, `infrastructure/helm/urumi/templates/wordpress.yaml` | Yes | WooCommerce remains the source of commerce state. |
| Order persists after pod restart | `infrastructure/helm/urumi/templates/pvc.yaml`, `infrastructure/helm/urumi/templates/mysql.yaml`, `infrastructure/helm/urumi/templates/wordpress.yaml` | Yes | PVCs are not backups. |
| WooCommerce MCP product/order/customer operations | `services/woo-mcp/app/tools/products.py`, `services/woo-mcp/app/tools/orders.py`, `services/woo-mcp/app/tools/customers.py` | Yes | Tools call WooCommerce REST. |
| User A creates a published product through chat | `services/gateway/app/api/chat.py`, `services/gateway/app/routing/router.py` | Yes | Provider uses an OpenAI-compatible endpoint. |
| User A asks about today's orders | `services/gateway/app/api/chat.py`, `services/gateway/app/routing/router.py` | Yes | The recorded question follows a manual storefront order. |
| Chat tool trace | `services/gateway/app/api/chat.py`, `dashboard/src` | Yes | Trace displays the tool calls made by the chat request. |
| User B connects from an external MCP client with gateway URL and API key | `services/gateway/app/mcp/server.py`, `services/gateway/app/auth/rbac.py` | Yes | The API key authenticates to Urumi; it is not forwarded as an upstream credential. |
| External client lists enabled upstream tools and answers orders question | `services/gateway/app/mcp/server.py`, `services/gateway/app/routing/router.py` | Yes | Disabled upstreams are removed from discovery. |
| One prompt calls WooCommerce and Currency | `services/gateway/app/api/chat.py`, `services/gateway/app/routing/router.py` | Yes | Recorded example: "Total today's orders and convert that total to EUR." |
| Tool permission filtering | `services/gateway/app/auth/rbac.py`, `services/gateway/app/routing/router.py`, `services/gateway/app/api/admin.py` | Yes | Permissions are checked during discovery and execution. |
| Disable upstream and remove its tools from both clients | `services/gateway/app/api/admin.py`, `services/gateway/app/routing/router.py` | Yes | Disabled upstream tools remain unavailable until re-enabled. |
| Revoke user B's key | `services/gateway/app/api/admin.py`, `services/gateway/app/auth/rbac.py` | Yes | Revocation uses the admin key-management workflow. |
| Upstream pod failure isolation and dashboard status | `services/gateway/app/mcp/client.py`, `services/gateway/app/routing/router.py`, `dashboard/src` | Yes | A failed upstream is marked unreachable; other upstreams remain usable. |
| Audit entries attributed to the initiating user | `services/gateway/app/routing/router.py`, `services/gateway/app/models/tables.py` | Yes | Attribution records the gateway user who initiated each call. |
| Three connected upstreams | `infrastructure/helm/urumi/templates/mcp-servers.yaml`, `services/woo-mcp`, `services/weather-mcp`, `services/currency-mcp` | Yes | WooCommerce MCP is written in-house. |
| OpenAI-compatible LLM configuration | `infrastructure/helm/urumi/values.yaml`, `infrastructure/helm/urumi/values-local.yaml`, `infrastructure/helm/urumi/templates/gateway.yaml`, `services/gateway/app/api/chat.py` | Yes | Local defaults are `https://openrouter.ai/api/v1` and `openrouter/free`; `secrets.llmApiKey` is empty by default. |
| Chart-identical production-like deployment procedure | `infrastructure/helm/urumi/values-prod.yaml`, `docs/store-deployment-runbook.md` | Documented path | Domain, registry, credentials, and TLS Secret are supplied at deployment time. |

## Related checks and configuration

The following commands are the repository's repeatable validation commands:

```powershell
helm lint infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
helm lint infrastructure/helm/urumi -f infrastructure/helm/urumi/values-prod.yaml
helm template urumi infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
helm template urumi infrastructure/helm/urumi -f infrastructure/helm/urumi/values-prod.yaml
kubectl get pods -o wide
kubectl get jobs
kubectl get pvc
kubectl get services
kubectl get ingress
```

The chat provider settings are `llm.baseUrl`, `llm.model`, and `secrets.llmApiKey`; the gateway receives the provider key as `LLM_API_KEY`. Local values use `https://openrouter.ai/api/v1` and `openrouter/free`.

## Known limitations

- The chart does not install cert-manager or issue a certificate; production values reference the `urumi-tls` Secret.
- Kubernetes Secret encryption at rest is not configured by the chart.
- `TOOL_CACHE` is in-memory per gateway process and replicas do not share cache invalidation.
- The SSRF validator does not block loopback IP literals; private and cluster IPs are allowed for in-cluster MCP endpoints.
- The gateway does not implement HTTP-level rate limits.
- PVCs are not backups.
