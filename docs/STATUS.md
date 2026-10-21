# Assignment evidence record

## Summary

The recorded local k3d run used `infrastructure/helm/urumi` with `values-local.yaml`. It demonstrated the store, chat agent, external MCP client, tool permissions, upstream control, key revocation, failure isolation, audit attribution, and persistence after pod restart. The same chart is documented for production-like deployment with `values-prod.yaml` and deployment-time configuration.

## Requirement-to-evidence record

| Requirement | Implementation (file path) | Verified (recorded local run) | Limitation |
|---|---|---|---|
| Root Helm chart and environment values | `infrastructure/helm/urumi/Chart.yaml`, `infrastructure/helm/urumi/values.yaml`, `infrastructure/helm/urumi/values-local.yaml`, `infrastructure/helm/urumi/values-prod.yaml` | Yes | Production DNS, registry, secrets, and TLS Secret are deployment inputs. |
| WordPress + WooCommerce store | `infrastructure/helm/urumi/templates/wordpress.yaml`, `infrastructure/helm/urumi/templates/mysql.yaml`, `infrastructure/helm/urumi/templates/wp-setup.yaml` | Yes | PVCs are not backups. |
| Checkout and order visibility | `services/woo-mcp/app/woocommerce.py`, `infrastructure/helm/urumi/templates/wordpress.yaml` | Yes | The recorded flow uses test data and COD. |
| Order persistence after pod restart | `infrastructure/helm/urumi/templates/pvc.yaml`, `infrastructure/helm/urumi/templates/mysql.yaml`, `infrastructure/helm/urumi/templates/wordpress.yaml` | Yes | PVC persistence does not provide backup/restore. |
| WooCommerce MCP product/order/customer tools | `services/woo-mcp/app/tools/products.py`, `services/woo-mcp/app/tools/orders.py`, `services/woo-mcp/app/tools/customers.py` | Yes | The service uses WooCommerce REST credentials; it does not query MySQL directly. |
| One gateway endpoint and namespaced upstream tools | `services/gateway/app/mcp/server.py`, `services/gateway/app/routing/router.py`, `services/gateway/app/routing/collisions.py` | Yes | `TOOL_CACHE` is process-local and replicas do not share invalidation. |
| Three upstream servers | `infrastructure/helm/urumi/templates/mcp-servers.yaml`, `services/woo-mcp`, `services/weather-mcp`, `services/currency-mcp` | Yes | WooCommerce is written in-house; Weather and Currency are separate upstream services. |
| Chat agent and product creation | `services/gateway/app/api/chat.py`, `dashboard/src` | Yes | Live provider calls require a valid provider key and reachable OpenAI-compatible endpoint. |
| Chat agent order lookup | `services/gateway/app/api/chat.py`, `services/gateway/app/routing/router.py` | Yes | Tool results depend on current store data and upstream availability. |
| External MCP client access as user B | `services/gateway/app/mcp/server.py`, `services/gateway/app/auth/rbac.py`, `services/gateway/app/api/admin.py` | Yes | Clients must send the gateway URL and a valid gateway API key. |
| Cross-upstream tool call | `services/gateway/app/api/chat.py`, `services/gateway/app/routing/router.py` | Yes | The recorded example combines WooCommerce order retrieval and Currency conversion. |
| Tool permissions at discovery and execution | `services/gateway/app/routing/router.py`, `services/gateway/app/auth/rbac.py`, `services/gateway/app/api/admin.py` | Yes | Permission changes apply to tools exposed by the gateway. |
| Upstream disable removes tools from both clients | `services/gateway/app/api/admin.py`, `services/gateway/app/routing/router.py` | Yes | A disabled upstream is unavailable until re-enabled. |
| API-key revocation | `services/gateway/app/auth/rbac.py`, `services/gateway/app/auth/api_keys.py`, `services/gateway/app/api/admin.py` | Yes | The revoke endpoint is admin-only. |
| Upstream failure isolation | `services/gateway/app/routing/router.py`, `services/gateway/app/mcp/client.py` | Yes | Timeouts do not eliminate every resource-exhaustion pattern. |
| Audit attribution | `services/gateway/app/routing/router.py`, `services/gateway/app/models/tables.py` | Yes | Audit attribution identifies the gateway user who initiated the call. |
| OpenAI-compatible LLM configuration | `infrastructure/helm/urumi/values.yaml`, `infrastructure/helm/urumi/values-local.yaml`, `infrastructure/helm/urumi/templates/gateway.yaml`, `services/gateway/app/api/chat.py` | Yes | Local defaults are `https://openrouter.ai/api/v1` and `openrouter/free`; `secrets.llmApiKey` is empty by default. |
| Secret references and network controls | `infrastructure/helm/urumi/templates/secrets.yaml`, `infrastructure/helm/urumi/templates/networkpolicy.yaml` | Yes | Kubernetes Secret encryption at rest is not configured by the chart. |
| Chart-identical production-like deployment procedure | `infrastructure/helm/urumi/values-prod.yaml`, `docs/store-deployment-runbook.md` | Documented path | Domain, registry, credentials, and TLS Secret are supplied by the deployment environment. |

## Recorded walkthrough

The screen-recorded local k3d demo is the evidence artifact. The walkthrough covers COD checkout, order persistence after pod restart, chat product creation and order lookup, external MCP access, a two-upstream prompt, tool permissions, upstream disable, key revocation, pod failure isolation, and audit attribution.

## Security and configuration

- `llm.baseUrl` and `llm.model` configure the provider endpoint and model.
- `secrets.llmApiKey` supplies the provider API key as `LLM_API_KEY`.
- Gateway client keys authenticate to Urumi; they are not passed through as upstream credentials.
- Local demo credentials in `infrastructure/helm/urumi/values-local.yaml` are throwaway values for the disposable local cluster.
- Production secrets are supplied through deployment-time `--set-string` overrides or an approved secret manager; no production secret exists in the repository.
- The chart does not install cert-manager, configure Kubernetes Secret encryption at rest, or provide HTTP-level rate limits.
