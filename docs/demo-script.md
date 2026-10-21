# Demo video script — Urumi MCP Gateway

**Target:** a concise, evidence-led walkthrough of the assignment deliverables. Walk through the completed assignment implementation in the local demo environment. Do not expose API keys, provider keys, passwords, or customer personal data.

## 1. Open with the assignment and repository

- Open the GitHub repository and point to the root Helm chart, service directories, tests, CI workflow, and docs.
- Explain the objective: one MCP gateway endpoint for multiple upstream servers, deployed with Kubernetes/Helm.
- State the assignment scope and show the implementation through the live application and Kubernetes resources.

## 2. Show Kubernetes deployment

Run and show the output of:

```powershell
kubectl get pods -o wide
kubectl get services
kubectl get ingress
kubectl get pvc
kubectl get jobs
```

Show the gateway, dashboard, Woo MCP, Weather MCP, Currency MCP, WordPress, MySQL and PostgreSQL workloads, including the completed setup Job and bound persistent claims.

## 3. Show the store

- Open `http://store.urumi.local`.
- Show a published demo product.
- If checkout is working, complete a test-only Cash on Delivery checkout and verify the order in wp-admin.
- Show the storefront/order workflow and persistence procedure from the acceptance guide.

## 4. Show dashboard and MCP aggregation

- Open `http://dashboard.urumi.local` and sign in with a valid **Urumi Gateway API key** (this is different from the OpenRouter/provider API key).
- Show server status and namespaced tools for WooCommerce, Weather and Currency.
- Connect MCP Inspector or another MCP client to the single gateway `/mcp` endpoint with a disposable member key.
- Run a harmless read operation first, such as listing products or orders.

## 5. Show authorization and audit

- Use a member key and show an admin-only operation is denied.
- If a tool permission is denied for the member role, show that it disappears from discovery and a direct call is rejected too.
- Show the matching audit record. Revoke the disposable key and demonstrate a subsequent request fails.

## 6. Show resilience and persistence (only if verified)

- Disable an upstream or stop its pod in the disposable demo cluster. Show the other upstreams still respond.
- If demonstrating persistence, record a product/order identifier, restart WordPress/MySQL pods without deleting PVCs, and confirm the data remains.

## 7. Close

Summarize the completed chart, gateway, store/MCP integration, authorization/audit controls, tests and documentation. Distinguish assignment scope from optional production hardening. Do not show secrets, private keys, invitation tokens, customer data or internal account information in the recording.
