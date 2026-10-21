# Live acceptance tests

These checks are for a disposable local cluster. Unit tests do not replace browser checkout or prove production readiness. Never commit credentials or show them in screenshots.

## 1. Helm rendering
```powershell
helm lint infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
helm lint infrastructure/helm/urumi -f infrastructure/helm/urumi/values-prod.yaml
helm template urumi infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
helm template urumi infrastructure/helm/urumi -f infrastructure/helm/urumi/values-prod.yaml
```
Review Secret references, PVCs, Ingress and NetworkPolicies. Rendering is not a successful installation.

## 2. Kubernetes state
```powershell
kubectl get pods -o wide
kubectl get jobs
kubectl get pvc
kubectl get services
kubectl get ingress
```
Verify that the workloads are Ready, the setup Job is complete, and database/content claims are Bound; these are the expected successful acceptance outcomes.

## 3. Store and persistence
1. Open the storefront and confirm a published test product.
2. Complete a test-only COD checkout.
3. Verify order, line items, total, payment method and status in wp-admin.
4. Record a product/order ID.
5. Restart WordPress and MySQL pods without deleting PVCs.
6. Confirm the same product/order remains.

Mark this gate complete only after actually observing each step.

## 4. WooCommerce MCP tool contract
Through the single gateway `/mcp` endpoint, confirm these registered WooCommerce tools are discoverable and callable:
- `get_products`: read product catalog, optionally search/paginate.
- `get_orders`: read orders with optional date/status/page filters.
- `create_order`: create a pending COD order from product IDs and positive quantities; WooCommerce calculates line-item prices.
- `get_customer`: retrieve a customer by numeric ID, returning a minimized profile.
- `get_order`: retrieve one order by ID.
- `create_product` and `update_order_status`: additional product/order operations.

Use a disposable store and test customer. For `create_order`, verify the returned order ID and then independently confirm that order in WooCommerce/wp-admin. The MCP order-creation operation is distinct from a storefront checkout.

## 5. WooCommerce REST smoke test
Use a disposable store and least-privilege REST key. Set `WOO_BASE_URL`, `WOO_CONSUMER_KEY` and `WOO_CONSUMER_SECRET` in the local shell without echoing values, then run:
```powershell
python scripts/smoke_test_woocommerce.py
```
Use the supported insecure-HTTP opt-in only for a local demo. Remove any disposable draft product after testing.

## 6. MCP, permissions and audit
Connect MCP Inspector or an SDK client to the single gateway `/mcp` endpoint using a disposable member key. Verify initialize, `tools/list` and a harmless `tools/call`. Confirm all three upstream namespaces appear. Verify member admin access is denied, denied tools are hidden and rejected on direct calls, and revoking the key blocks the next request. Check audit events for caller/server/tool/duration/outcome.

## 7. Failure isolation
The acceptance flow demonstrates that disabling an upstream removes its tools and stale calls fail, while healthy upstreams remain usable.

## 8. Dashboard/chat
Sign in with a Urumi Gateway API key; this is distinct from the LLM provider key. Chat uses `LLM_BASE_URL`, `LLM_MODEL`, and `LLM_API_KEY` for an OpenAI-compatible chat-completions provider (for example OpenRouter). The base URL/model are non-secret Helm values; the API key is injected from a Kubernetes Secret. Missing provider configuration should produce a clear configuration error, not a pretend live model result.
