# Assignment deliverables and evidence matrix

This matrix maps assignment deliverables to repository artifacts and the proof to show in a walkthrough. Source presence is not equivalent to runtime acceptance.

| Deliverable | Repository evidence | Demonstration / acceptance proof |
|---|---|---|
| Root Helm chart | `infrastructure/helm/urumi/Chart.yaml`, shared/local/production values and templates | Run `helm lint` and `helm template` with local and production values |
| Kubernetes workloads | Gateway, dashboard, MCP servers, WordPress, MySQL, PostgreSQL templates | Show pods Ready, Services/Ingress and setup Job completion |
| Persistent storage | `templates/pvc.yaml`, MySQL/Postgres/WordPress claims | Record a product/order, restart relevant pods without deleting PVCs, confirm data persists |
| WooCommerce store | WordPress/WooCommerce setup template and runbook | Storefront product, COD checkout and order visible in wp-admin |
| WooCommerce MCP tools | `services/woo-mcp/app/tools/products.py`, `orders.py`, `customers.py` | Discover and call `list_products`, `get_products` (alias), `create_product`, `list_orders`, `get_orders` (alias), `create_order`, `get_order`, `update_order_status`, and `get_customer` |
| Single MCP endpoint | Gateway MCP server and router | MCP client connects to one `/mcp` endpoint and lists namespaced tools from all upstreams |
| Multi-upstream routing | Woo, Weather, Currency MCP services | Show calls from multiple upstreams via gateway; show healthy services continue when one fails |
| Auth and RBAC | Gateway auth, API keys, role checks, permissions | Admin route rejected for member; denied tool is hidden and rejected on direct call |
| Key lifecycle | API key creation/revocation endpoints | Revoke a test key and show next request rejected; revocation endpoint is admin-only |
| Audit trail | Audit service and API | Show caller, server, tool, duration, outcome for test calls |
| Dashboard/chat | `dashboard/src`, gateway chat API and provider-neutral LLM settings | Sign in with a Urumi gateway key; verify chat through configured `llm.baseUrl`, `llm.model`, and Secret-backed `secrets.llmApiKey` |
| Secrets and isolation | Helm Secret template, NetworkPolicies, threat model | Verify no real credentials in Git, no public database/MCP ingress, and policies render correctly |
| CI and tests | `.github/workflows/ci.yml`, `tests/` | Show successful CI/test results for the exact published commit |
| Documentation/video | README and `docs/*.md` | Explain architecture, setup, security decisions, limitations, and show the actual running system |

## Walkthrough evidence order

1. Show the published repository and green CI run for the exact commit being evaluated.
2. Show the Helm chart, values, Secret references, PVCs, Services, Ingress and NetworkPolicies.
3. Show the running store/dashboard and a WooCommerce order verified in wp-admin.
4. Show the single gateway endpoint and namespaced tools from WooCommerce, Weather and Currency.
5. Demonstrate WooCommerce tools, role/tool authorization, key revocation, audit records, and failure isolation.
6. Show existing recordings only for the flows they demonstrate. Do not claim a persistence/restart check unless that exact action is visible in a recording or separately recorded as observed.
7. Distinguish automated test results, existing live-demo evidence, and acceptance gates that have not been run.

## Reference implementations

Reference projects informed product concepts such as a single endpoint, registry/health UI, auditability and network-edge controls. This repository's code is its own implementation; reference projects are not runtime dependencies. Acceptance criteria and actual evidence take priority over feature imitation.
