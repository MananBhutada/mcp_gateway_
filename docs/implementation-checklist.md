# Implementation and submission checklist

Use this checklist as the single final acceptance tracker. Check an item only after the described evidence has been observed. A code file or passing unit test alone does not prove the live end-to-end behavior.

## A. GitHub and submission
- [x] Source project and initial documentation published to `MananBhutada/mcp_gateway_` on `main`.
- [ ] README describes the assignment, architecture, setup, security, limitations and docs index.
- [ ] All Markdown documents reviewed for current status and consistency.
- [ ] GitHub Actions results inspected for the published commit.
- [ ] Demo video recorded with no credentials or personal data exposed.

## B. Helm and Kubernetes
- [ ] `helm lint` passes with local values.
- [ ] `helm lint` passes with production values.
- [ ] `helm template` succeeds with both values files.
- [ ] Live cluster has expected workloads Ready, setup Job completed and PVCs Bound.
- [ ] Public Ingress is limited to dashboard and storefront.
- [ ] NetworkPolicies are rendered and live behavior reviewed.
- [ ] Production values use unique secrets, TLS and suitable persistent storage.

## C. WordPress/WooCommerce
- [ ] WooCommerce setup is successful on a clean local install.
- [ ] Published test product visible through storefront.
- [ ] Test COD checkout completed and order verified in wp-admin.
- [ ] WordPress and MySQL pods restarted without deleting PVCs; product/order still present.
- [ ] WooCommerce REST smoke test succeeds using disposable least-privilege credentials.

## D. WooCommerce MCP
- [ ] Product list/read/create behavior verified against the real store.
- [ ] Order list/read/update behavior verified against a disposable test order.
- [ ] Invalid inputs, HTTP failures and timeouts return safe errors.
- [ ] Woo MCP is not publicly exposed and is authenticated from its caller.

## E. Gateway and upstreams
- [ ] One `/mcp` endpoint returns tools from WooCommerce, Weather and Currency.
- [ ] MCP client successfully initializes, lists tools and calls a tool.
- [ ] Tool names are namespaced and collisions are handled.
- [ ] Unavailable upstream does not block healthy upstream calls.
- [ ] Disabled upstream tools disappear and stale calls are rejected.

## F. Authentication, permissions and audit
- [ ] Admin/member roles enforced by backend on admin APIs.
- [ ] API keys shown once, stored as hashes, and revocable.
- [ ] Member denied access to admin-only APIs.
- [ ] Member cannot execute a tool denied by permission policy.
- [ ] Successful and failed tool calls are audited with user/server/tool/duration/outcome.
- [ ] Invitation expiry and one-time acceptance behavior verified.

## G. Dashboard and chat
- [ ] Dashboard authenticates using a Urumi gateway key.
- [ ] Server/tool/permission views reflect backend data.
- [ ] Chat provider key configured through runtime secret injection, not committed.
- [ ] Chat tool calls go through the gateway and are attributed to the user.

## H. Final demo readiness
- [ ] Repository and architecture shown first.
- [ ] Live deployment, storefront, dashboard and one MCP call shown.
- [ ] Authorization and audit demonstrated.
- [ ] Persistence/failure isolation demonstrated if verified.
- [ ] Every unverified item described as pending rather than claimed complete.

## Recommended order

1. Run Helm lint/template for both values files.
2. Check current cluster health and run the live MCP read-only check.
3. Confirm store/MCP behavior and permission enforcement.
4. Capture persistence/failure-isolation evidence.
5. Inspect CI, then record the video using `docs/demo-script.md`.
