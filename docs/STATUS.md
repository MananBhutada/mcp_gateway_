# Assignment implementation status

## Current status

The repository contains the assignment's core architecture and deployment artifacts. Source code defines the WooCommerce MCP tools, gateway routing and authorization, dashboard APIs, Helm resources, and OpenAI-compatible chat configuration. Source presence is not proof that a feature works in the live cluster. Report live acceptance only when the exact check has been observed and recorded.

## Delivered implementation

| Requirement | Repository evidence |
|---|---|
| Root Helm chart and environment values | `infrastructure/helm/urumi`, `values.yaml`, `values-local.yaml`, `values-prod.yaml` |
| Persistent database and store | MySQL with PVC; WordPress + WooCommerce with persistent content; PostgreSQL with PVC for gateway control-plane data |
| WooCommerce MCP tools | `list_products`, `get_products` (alias), `create_product`, `list_orders`, `get_orders` (alias), `create_order`, `get_order`, `update_order_status`, `get_customer`; see `services/woo-mcp/app/tools/` |
| Unified MCP gateway | Single `/mcp` endpoint aggregating WooCommerce, Weather and Currency tools with namespaced tool names |
| Dashboard/control plane | React dashboard and gateway APIs for server status, users/keys, permissions, audit, and chat integration |
| Provider configuration | `llm.baseUrl` and `llm.model` are non-secret Helm values; `secrets.llmApiKey` is injected as `LLM_API_KEY`; chat calls an OpenAI-compatible chat-completions endpoint |
| Local provider defaults | `values-local.yaml` sets `https://openrouter.ai/api/v1` and `openrouter/free`; `secrets.llmApiKey` is empty by default |
| Security boundaries | Kubernetes Secret references, API-key authentication, server-side role/tool authorization, upstream timeouts and NetworkPolicies |
| Verification and handoff | Gateway/Woo MCP tests, Helm checks, integration scripts, threat model, runbook, architecture docs, acceptance guide and demo script |
| Source delivery | [`MananBhutada/mcp_gateway_`](https://github.com/MananBhutada/mcp_gateway_) |

## Verification status

The chat implementation in `services/gateway/app/api/chat.py` reads `LLM_BASE_URL`, `LLM_MODEL`, and `LLM_API_KEY`, calls an OpenAI-compatible `/chat/completions` endpoint, and routes model-requested tools through the authenticated gateway router. This is verified in code. A successful live provider request requires valid deployment configuration and must be observed separately.

The repository contains tests and a CI workflow. Confirm the CI result for the exact commit being reviewed before reporting CI as passing. Do not use test results from a different commit as evidence for the current branch.

## Existing demo evidence

The project owner reports recordings of the storefront COD order and admin verification, admin-side order query, Weather/Currency chat, MCP Inspector order listing, API-key revocation, dashboard server status, upstream failure isolation/recovery, and tool visibility when a server is disabled/re-enabled. These recordings establish only the actions actually visible in each recording. They do not establish clean-install behavior or pod-restart persistence unless those actions appear in the relevant recording.

## Final acceptance gates

1. Confirm CI passes for the exact submitted commit, including gateway tests, Woo MCP tests, dashboard build and local/production Helm validation.
2. Through the gateway `/mcp` endpoint, discover and call the required product/order operations and verify any created product/order independently in WooCommerce.
3. Verify Helm rendering references the provider URL/model and Secret-backed API key without exposing the key in manifests or Git.
4. Use existing recordings only for the flows they show; separately run and record any still-required persistence/restart check in the disposable local cluster.
5. Verify member/admin authorization, direct tool-call denial, key revocation, audit attribution and upstream failure isolation in the target deployment.

## Security note

Never commit real credentials or put keys, passwords, invitation tokens, or customer personal data in screenshots or video. Local values are disposable development-only values. Production secrets must be supplied at deployment time or managed through an approved secret manager. The chart does not configure Kubernetes Secret encryption at rest or cert-manager.
