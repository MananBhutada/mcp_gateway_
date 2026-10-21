# Live acceptance tests

These checks are for a disposable local cluster. Unit tests do not replace browser checkout or prove production readiness. Never commit credentials or show them in screenshots.

## 1. Helm rendering

~~~~powershell
helm lint infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
helm lint infrastructure/helm/urumi -f infrastructure/helm/urumi/values-prod.yaml
helm template urumi infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
helm template urumi infrastructure/helm/urumi -f infrastructure/helm/urumi/values-prod.yaml
~~~~

Review Secret references, PVCs, Ingress and NetworkPolicies. Rendering is not a successful installation.

## 2. Kubernetes state

~~~~powershell
kubectl get pods -o wide
kubectl get jobs
kubectl get pvc
kubectl get services
kubectl get ingress
~~~~

Verify workloads are Ready, the setup Job is complete, and database/content claims are Bound. These are expected acceptance outcomes, not a claim that the commands were run for every commit.

## 3. Store and persistence

1. Open the storefront and confirm a published test product.
2. Complete a test-only COD checkout.
3. Verify order, line items, total, payment method and status in wp-admin.
4. Record a product/order ID.
5. Restart WordPress and MySQL pods without deleting PVCs.
6. Confirm the same product/order remains.

Mark this gate complete only after actually observing each step.

## 4. WooCommerce MCP tool contract

The source registers these WooCommerce tools in `services/woo-mcp/app/tools/`:

- `list_products`: canonical product-list tool.
- `get_products`: alias of `list_products`.
- `create_product`: creates a simple product; status defaults to `draft`, and `status="publish"` makes it visible on the storefront.
- `list_orders`: canonical order-list tool with optional after/status/page-size filters.
- `get_orders`: alias of `list_orders`.
- `create_order`: creates a pending, unpaid COD order from product IDs and positive quantities.
- `get_order`: retrieves one order by numeric ID.
- `update_order_status`: changes an order to a supported WooCommerce status.
- `get_customer`: retrieves a minimized customer profile by numeric ID.

Through the single gateway `/mcp` endpoint, verify every tool is discoverable and callable. Use a disposable store and test customer. For `create_order`, verify the returned order ID and independently confirm that order in WooCommerce/wp-admin. The MCP order-creation operation is distinct from a storefront checkout. **Needs live run** unless evidence for the exact tool call is recorded.

## 5. WooCommerce REST smoke test

Use a disposable store and least-privilege REST key. Set `WOO_BASE_URL`, `WOO_CONSUMER_KEY` and `WOO_CONSUMER_SECRET` in the local shell without echoing values, then run:

~~~~powershell
python scripts/smoke_test_woocommerce.py
~~~~

Use the supported insecure-HTTP opt-in only for a local demo. Remove any disposable draft product after testing.

## 6. MCP, permissions and audit

Connect MCP Inspector or an SDK client to the single gateway `/mcp` endpoint using a disposable member key. Verify initialize, `tools/list` and a harmless `tools/call`. Confirm all three upstream namespaces appear. Verify member admin access is denied, denied tools are hidden and rejected on direct calls, and revoking a key blocks the next request. Check audit events for caller/server/tool/duration/outcome. **Needs live run** for each behavior not supported by evidence from the exact deployment.

## 7. Failure isolation

Disable one upstream and verify its tools disappear while healthy upstreams remain usable. Alternatively, stop a disposable upstream pod and observe recovery. Do not delete PVCs as part of this test. **Needs live run** unless the exact action and outcome are visible in an existing recording.

## 8. Dashboard/chat

Sign in with a Urumi Gateway API key; this is distinct from the LLM provider key. Chat reads Helm values `llm.baseUrl` and `llm.model`, and the Secret-backed `secrets.llmApiKey` becomes `LLM_API_KEY`. The gateway calls an OpenAI-compatible chat-completions endpoint; local values set `https://openrouter.ai/api/v1` and `openrouter/free`, while the provider key is empty by default. A live provider call requires a valid key and a reachable model. Missing provider configuration should return a configuration error, not a pretend live model result. **Needs live run** for actual provider success.
