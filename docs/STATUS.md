# Implementation status and evidence

This file separates implemented code from evidence observed in a running environment. Do not mark a gate complete solely because a file or test exists.

## Repository implementation

- Root Helm chart: `infrastructure/helm/urumi`, with shared, local, and production values.
- Services: gateway, WooCommerce MCP, Weather MCP, Currency MCP, dashboard, WordPress/WooCommerce, MySQL, PostgreSQL.
- Gateway features: API-key authentication, role/tool authorization, namespaced aggregation, server registry, audit trail, upstream timeouts/failure isolation, and chat integration.
- Store persistence: MySQL and WordPress PVCs; gateway control-plane data uses PostgreSQL/PVC.
- Verification: CI workflow, gateway and Woo MCP tests, Helm template test(s), and local integration scripts.

## Evidence recorded in project work

The developer's local k3d environment previously had the `k3d-urumi` cluster running, with the `store.urumi.local` and `dashboard.urumi.local` hosts returning HTTP 200. Deployments observed included gateway, dashboard, MySQL, PostgreSQL, WordPress, WooCommerce MCP, Weather MCP, and Currency MCP; the database/content PVCs were present. WooCommerce 9.9.5 was installed. A live read-only check reported three connected upstream servers and nine tools. Woo MCP unit tests had 21 passing tests; gateway tests had 22 passing with one deselected; Helm tests had two passing; the dashboard build succeeded.

These are recorded prior-session observations, not a guarantee that the current cluster is still running or that every acceptance gate has passed. Re-run the relevant commands before recording the demo.

## Required final verification

| Gate | Evidence to capture | State in this handoff |
|---|---|---|
| Source repository | GitHub `main` points to the published assignment commit; docs and source visible | Published |
| Gateway / dashboard | Health endpoint, dashboard login with a valid gateway key, API response | Recheck before recording |
| MCP aggregation | `tools/list` shows WooCommerce, Weather, Currency tools through one endpoint | Previously observed; recheck |
| WooCommerce | Product/order tools against the deployed store; browser checkout if required | Recheck live |
| Auth and permissions | Admin/member separation, denied tool hidden and rejected, revoked key rejected | Recheck live |
| Audit | Successful and failed tool calls have attributable audit events | Recheck live |
| Helm | lint and template for both local and production values | Run against published commit |
| Persistence | Record product/order, restart WordPress/MySQL pods (not PVCs), verify data remains | Recheck live |
| CI | GitHub Actions results for the published commit | Inspect Actions |
| Demo video | Real application shown; no credentials exposed; claims match evidence | Pending recording |

## Safety and limitations

Never paste live credentials into this file. Keep the status honest: distinguish a unit test, rendered manifest, live local-cluster check, and production-like deployment. A local k3d pass does not prove a VPS/k3s deployment.
