# Live acceptance tests

These checks are intended for a disposable local cluster. They complement unit tests; they do not replace a real browser checkout or prove production readiness. Never put credentials into command history, logs, screenshots or Git.

## 1. Helm rendering

```powershell
helm lint infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
helm lint infrastructure/helm/urumi -f infrastructure/helm/urumi/values-prod.yaml
helm template urumi infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
helm template urumi infrastructure/helm/urumi -f infrastructure/helm/urumi/values-prod.yaml
```

Review rendered Secret references, PVCs, Ingress, resource settings and NetworkPolicies. Rendering is not the same as a successful installation.

## 2. Live Kubernetes state

```powershell
kubectl get pods -o wide
kubectl get jobs
kubectl get pvc
kubectl get services
kubectl get ingress
```

Expected: application pods Ready, WordPress setup Job complete, and MySQL/PostgreSQL/WordPress PVCs Bound. Inspect events and logs before retrying a failed Job.

## 3. Store and persistence

1. Open the configured storefront hostname and confirm a published test product.
2. Complete a test-only COD checkout.
3. Verify order number, line items, total, payment method and status in wp-admin.
4. Record a product/order ID.
5. Restart WordPress and MySQL pods only; do not delete PVCs.
6. Verify the same product/order remains.

Mark this gate complete only after the browser and post-restart checks have actually passed.

## 4. WooCommerce REST smoke test

Use a disposable store and least-privilege REST key. Set `WOO_BASE_URL`, `WOO_CONSUMER_KEY`, and `WOO_CONSUMER_SECRET` in the local shell without echoing or committing them, then run:

```powershell
python scripts/smoke_test_woocommerce.py
```

For a local HTTP cluster only, use the explicit insecure-HTTP opt-in supported by the script. The smoke test should use a disposable draft product; remove it manually after testing. Never use production customer/order data.

## 5. MCP gateway

Connect MCP Inspector or an SDK client to the single gateway `/mcp` endpoint with a disposable member key. Verify initialize, `tools/list`, and a harmless `tools/call`. Confirm WooCommerce, Weather and Currency tools are namespaced and that the call is audited. Revoke the key and verify the next call is rejected.

## 6. Authorization, audit and isolation

- Verify member key receives 403 on admin-only API routes.
- Deny a specific tool for MEMBER; verify it is hidden from the member's tool list and rejected on direct call.
- Verify audit events contain user, server, tool, duration and outcome for success and failure.
- Disable an upstream and verify its tools disappear; try a stale call.
- In a disposable cluster, stop one upstream and confirm other upstreams remain usable.

## 7. Dashboard and chat

Sign in using a Urumi Gateway API key, not the LLM provider key. Chat additionally requires a configured provider key. Verify a tool-calling prompt uses gateway routing and audit attribution. If the provider key is absent, a clear configuration error is expected; do not present a mocked answer as a live model result.
