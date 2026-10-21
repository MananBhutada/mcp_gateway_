# Implementation and submission checklist

Check an item only after the described evidence has been observed. A file or unit test alone does not prove live end-to-end behavior.

## A. GitHub and submission
- [x] Source project published to `MananBhutada/mcp_gateway_` on `main`.
- [x] README and assignment handoff documentation updated.
- [ ] Inspect GitHub Actions results for the published commit.
- [ ] Record the demo video without exposing credentials or personal data.

## B. Helm and Kubernetes
- [ ] `helm lint` passes with local values.
- [ ] `helm lint` passes with production values.
- [ ] `helm template` succeeds with both values files.
- [ ] Expected workloads are Ready, setup Job completed and PVCs Bound.
- [ ] Public Ingress is limited to dashboard and storefront.
- [ ] Rendered and live NetworkPolicies are reviewed.
- [ ] Production values use unique secrets, TLS and persistent storage.

## C. WordPress/WooCommerce
- [ ] Published test product visible in storefront.
- [ ] Test COD checkout completed and order verified in wp-admin.
- [ ] WordPress and MySQL pods restarted without deleting PVCs; product/order remains.
- [ ] WooCommerce REST smoke test succeeds with disposable least-privilege credentials.

## D. WooCommerce MCP and gateway
- [ ] Product and order tools verified against the real store.
- [ ] One `/mcp` endpoint returns namespaced WooCommerce, Weather and Currency tools.
- [ ] MCP client initializes, lists tools and calls a tool.
- [ ] Unavailable upstream does not block healthy upstream calls.
- [ ] Disabled upstream tools disappear and stale calls are rejected.

## E. Authentication, authorization and audit
- [ ] Admin/member roles enforced server-side.
- [ ] API keys are shown once, stored hashed and revocable.
- [ ] Member is denied admin APIs and denied tools at execution time.
- [ ] Successful and failed calls produce attributable audit events.
- [ ] Invitation expiry and one-time acceptance are verified.

## F. Dashboard and chat
- [ ] Dashboard uses a Urumi Gateway API key for sign-in.
- [ ] Chat provider key is supplied through runtime configuration, never committed.
- [ ] Chat calls tools through the gateway and audit records attribute the user.

## G. Final demo
- [ ] Show repository, chart, running workloads, storefront, dashboard and one MCP call.
- [ ] Demonstrate authorization/audit and persistence/failure isolation if verified.
- [ ] Clearly label unverified items as pending rather than claiming they passed.

## Recommended order
1. Run Helm lint/template for both values files.
2. Check current cluster health and perform read-only MCP checks.
3. Verify WooCommerce, permissions and audit.
4. Capture persistence/failure-isolation evidence.
5. Inspect CI, then record using `docs/demo-script.md`.
