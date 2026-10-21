# Assignment deliverables and evidence matrix

This matrix maps the assignment deliverables to repository artifacts and the proof to show in a walkthrough. Source presence is not equivalent to runtime acceptance.

| Deliverable | Repository evidence | Demonstration / acceptance proof |
|---|---|---|
| Root Helm chart | `infrastructure/helm/urumi/Chart.yaml`, shared/local/production values and templates | Run `helm lint` and `helm template` with local and production values |
| Kubernetes workloads | Gateway, dashboard, MCP servers, WordPress, MySQL, PostgreSQL templates | Show pods Ready, Services/Ingress and setup Job completion |
| Persistent storage | `templates/pvc.yaml`, MySQL/Postgres/WordPress claims | Record a product/order, restart relevant pods without deleting PVCs, confirm data persists |
| WooCommerce store | WordPress/WooCommerce setup template and runbook | Storefront product, COD checkout and order visible in wp-admin; use the recorded storefront/order workflow |
| Required Woo MCP operations | `services/woo-mcp/app/tools`: `get_products`, `get_orders`, `create_order`, `get_customer` | Discover and call each required tool through the gateway; verify an MCP-created order independently in WooCommerce |
| Additional Woo operations | Product creation, single-order lookup, order-status update | Call only against disposable test data and verify results in the store |
| Single MCP endpoint | Gateway MCP server/client and router | MCP client connects to one `/mcp` endpoint and lists namespaced tools from all upstreams |
| Multi-upstream routing | Woo, Weather, Currency MCP services | Show tool calls from more than one upstream via gateway; show healthy services continue when one fails |
| Auth and RBAC | Gateway auth, API keys, role checks, permissions | Admin route rejected for member; allowed tool works; denied tool is hidden and rejected on direct call |
| Key lifecycle | API key creation/revocation endpoints | Revoke a test key and show next request rejected |
| Audit trail | Audit service and API | Show caller, server, tool, duration, outcome for test calls |
| Dashboard/chat | `dashboard/src`, gateway chat API and provider-neutral LLM settings | Sign in with a Urumi gateway key; verify chat through configured `LLM_BASE_URL`, `LLM_MODEL`, and Secret-backed `LLM_API_KEY` |
| Secrets and isolation | Helm Secret template, NetworkPolicies, threat model | Verify no real credentials in Git, no public database/MCP ingress, and policies render correctly |
| CI and tests | `.github/workflows/ci.yml`, `tests/` | Show successful CI/test results for the exact published commit |
| Documentation/video | README and `docs/*.md` | Explain architecture, setup, security decisions, limitations, and show the actual running system |

## Walkthrough evidence order

1. Show the published repository and current green CI run for the exact commit being evaluated.
2. Show the Helm chart, values, Secret references, PVCs, Services, Ingress and NetworkPolicies.
3. Show the running store/dashboard and a WooCommerce order verified in wp-admin.
4. Show the single gateway endpoint and namespaced tools from WooCommerce, Weather and Currency.
5. Demonstrate required Woo tools, role/tool authorization, key revocation, audit records, and failure isolation.
6. Show the existing recordings that cover those flows. Do not claim a persistence/restart check unless that exact action is visible in a recording or separately recorded as observed.
7. Distinguish automated test results, existing live-demo evidence, and any acceptance gate not yet run.

## Reference implementations

The implementation is organized around the assignment requirements. Reference projects informed the product concepts (single endpoint, registry/health UI, auditability and network-edge controls). This repository's code is its own implementation; reference projects are not runtime dependencies. Acceptance criteria and actual evidence take priority over feature imitation.
