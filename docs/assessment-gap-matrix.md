# Requirement-to-evidence matrix

This matrix maps the assignment requirements to implementation paths and the recorded local k3d walkthrough. The demo video is the evidence artifact; its link is maintained in `README.md`.

| Requirement | Implementation (file path) | Verified (recorded local run) | Limitation |
|---|---|---|---|
| Root Helm chart and values | `infrastructure/helm/urumi/Chart.yaml`, `infrastructure/helm/urumi/values.yaml`, `infrastructure/helm/urumi/values-local.yaml`, `infrastructure/helm/urumi/values-prod.yaml` | Yes | Production domain, registry, credentials, and TLS Secret are deployment inputs. |
| Kubernetes workloads | `infrastructure/helm/urumi/templates/gateway.yaml`, `dashboard.yaml`, `mcp-servers.yaml`, `wordpress.yaml`, `mysql.yaml`, `postgres.yaml` | Yes | The production procedure uses the same chart with production values. |
| Persistent store | `infrastructure/helm/urumi/templates/pvc.yaml`, `mysql.yaml`, `wordpress.yaml` | Yes | PVCs are not backups. |
| Storefront COD checkout | `infrastructure/helm/urumi/templates/wordpress.yaml`, `infrastructure/helm/urumi/templates/wp-setup.yaml` | Yes | Demonstrated with disposable test data. |
| Order persists after pod restart | `infrastructure/helm/urumi/templates/pvc.yaml`, `infrastructure/helm/urumi/templates/mysql.yaml`, `infrastructure/helm/urumi/templates/wordpress.yaml` | Yes | Persistence does not replace a backup/restore plan. |
| WooCommerce MCP tools | `services/woo-mcp/app/tools/products.py`, `services/woo-mcp/app/tools/orders.py`, `services/woo-mcp/app/tools/customers.py` | Yes | REST-backed operations use configured WooCommerce credentials. |
| One authenticated MCP endpoint | `services/gateway/app/mcp/server.py`, `services/gateway/app/auth/rbac.py` | Yes | Clients send the gateway URL and their own gateway API key. |
| WooCommerce, Weather, and Currency upstreams | `infrastructure/helm/urumi/templates/mcp-servers.yaml`, `services/woo-mcp`, `services/weather-mcp`, `services/currency-mcp` | Yes | `TOOL_CACHE` is in-memory per gateway process. |
| Chat creates and publishes a product | `services/gateway/app/api/chat.py`, `services/gateway/app/routing/router.py` | Yes | Provider calls use an OpenAI-compatible endpoint. |
| Chat answers orders question | `services/gateway/app/api/chat.py`, `services/gateway/app/routing/router.py` | Yes | The response uses current WooCommerce order data. |
| External MCP client, user B | `services/gateway/app/mcp/server.py`, `services/gateway/app/auth/rbac.py` | Yes | User B's key is a gateway API key, not an LLM provider key. |
| Prompt using two upstreams | `services/gateway/app/api/chat.py`, `services/gateway/app/routing/router.py` | Yes | The recorded example combines WooCommerce order totals and Currency conversion. |
| Tool permission filtering | `services/gateway/app/routing/router.py`, `services/gateway/app/auth/rbac.py`, `services/gateway/app/api/admin.py` | Yes | The permission model governs discovery and execution. |
| Upstream disable in both clients | `services/gateway/app/api/admin.py`, `services/gateway/app/routing/router.py` | Yes | Disabled upstream tools are removed from discovery. |
| Revoke B's key | `services/gateway/app/api/admin.py`, `services/gateway/app/auth/rbac.py` | Yes | Key revocation is performed through the admin workflow. |
| Upstream pod failure isolation | `services/gateway/app/mcp/client.py`, `services/gateway/app/routing/router.py` | Yes | Timeouts do not eliminate every resource-exhaustion pattern. |
| Audit attribution | `services/gateway/app/routing/router.py`, `services/gateway/app/models/tables.py` | Yes | Audit identity is the authenticated gateway user. |
| OpenAI-compatible provider config | `infrastructure/helm/urumi/values.yaml`, `infrastructure/helm/urumi/values-local.yaml`, `services/gateway/app/api/chat.py` | Yes | Local defaults are `https://openrouter.ai/api/v1` and `openrouter/free`; the local provider key is empty by default. |
| Secret references and NetworkPolicies | `infrastructure/helm/urumi/templates/secrets.yaml`, `infrastructure/helm/urumi/templates/networkpolicy.yaml` | Yes | Kubernetes Secret encryption at rest is not configured by the chart. |
| Chart-identical production deployment path | `infrastructure/helm/urumi/values-prod.yaml`, `docs/store-deployment-runbook.md` | Documented path | A specific VPS provisioning is not part of the recorded local run. |

## Walkthrough order

1. Show the storefront COD order and the same order in WooCommerce admin.
2. Show the order remains after a pod restart.
3. Show user A creating a published product through chat, then asking about today's orders with tool calls in the trace.
4. Connect user B's external MCP client using the gateway URL and B's API key; list tools and ask the same orders question.
5. Run the example prompt "Total today's orders and convert that total to EUR" to show WooCommerce and Currency tool calls.
6. Disable an upstream and show its tools disappear from chat and the external client.
7. Revoke B's key and show B's next call rejected.
8. Delete one upstream pod and show the other upstreams continue to work while the dashboard marks the failed upstream unreachable.
9. Show audit entries attributed to the correct users.

## Related documentation

- `README.md` — single entry point and full walkthrough.
- `docs/STATUS.md` — assignment evidence record.
- `docs/live-acceptance-tests.md` — requirement-level acceptance evidence.
- `docs/system-design.md` — routing, state, scaling, and deployment trade-offs.
- `docs/threat-model.md` — security boundaries and known limitations.
