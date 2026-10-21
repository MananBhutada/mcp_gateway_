# Assignment deliverables and evidence matrix

This matrix maps the Urumi AI FDE Round 1 brief to repository artifacts and the proof to show in a walkthrough. Source presence is not equivalent to runtime acceptance.

| Deliverable | Repository evidence | Demonstration / acceptance proof |
|---|---|---|
| Root Helm chart | `infrastructure/helm/urumi/Chart.yaml`, `values.yaml`, `values-local.yaml`, `values-prod.yaml`, templates | Run `helm lint` and `helm template` with local and production values |
| Kubernetes workloads | Gateway, dashboard, MCP servers, WordPress, MySQL, PostgreSQL templates | Show pods Ready, Services/Ingress and setup Job completion |
| Persistent storage | `templates/pvc.yaml`, MySQL/Postgres/WordPress claims | Record a product/order, restart relevant pods without deleting PVCs, confirm data persists |
| WooCommerce store | WordPress/WooCommerce setup template and runbook | Storefront product, cart/checkout and order visible in wp-admin; show the recorded storefront and order workflow in the demo |
| Candidate-written Woo MCP | `services/woo-mcp/app`, `tests/woo_mcp` | List and call product/order tools through the gateway against the real local store |
| Single MCP endpoint | Gateway MCP server/client and router | MCP client connects to one `/mcp` endpoint and lists namespaced tools from all upstreams |
| Multi-upstream routing | Woo, Weather, Currency MCP services | Show tool calls from more than one upstream via gateway; show healthy services continue when one fails |
| Auth and RBAC | Gateway auth, API keys, role checks, permissions | Admin route rejected for member; allowed tool works; denied tool is hidden and rejected on direct call |
| Key lifecycle | API key creation/revocation endpoints | Revoke a test key and show next request rejected |
| Audit trail | Audit service and API | Show caller, server, tool, duration, outcome for test calls |
| Dashboard/chat | `dashboard/src`, gateway chat API | Dashboard login uses a Urumi gateway key; chat requires a configured provider key and routes tools through gateway |
| Secrets and isolation | Helm Secret template, NetworkPolicies, threat model | Verify no real credentials in Git, no public database/MCP ingress, and policies render correctly |
| CI and tests | `.github/workflows/ci.yml`, `tests/` | Show successful CI/test results for the published commit |
| Documentation/video | README and all `docs/*.md` | Explain architecture, setup, security decisions, limitations, and show the actual running system |

## What the video should establish

1. The code and chart are in the published GitHub repository.
2. The application is running in Kubernetes, not only mocked locally.
3. A single gateway endpoint aggregates the upstream tools.
4. Authorization is enforced at execution time, not just hidden in the UI.
5. Store/database persistence and failure isolation are demonstrated or clearly marked as demonstrated through the documented acceptance flow.
6. The narration distinguishes tested behavior from design intent.

## Reference implementations

The implementation is organized around the assignment requirements. Reference projects informed the product concepts (single endpoint, registry/health UI, auditability and network-edge controls). This repository's code is its own implementation; reference projects are not runtime dependencies. Acceptance criteria and actual evidence take priority over feature imitation.
