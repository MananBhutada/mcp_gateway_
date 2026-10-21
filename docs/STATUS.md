# Assignment implementation status

## Current status

The repository contains the assignment's core architecture and deployment artifacts. The WooCommerce MCP contract now includes the named product/order/customer operations, and the gateway chat implementation uses a provider-neutral OpenAI-compatible API configured through Helm. Final completion should be claimed only after the CI workflow for the exact submitted commit is green and any required live acceptance checks are backed by recorded evidence.

## Delivered implementation

| Requirement | Repository evidence |
|---|---|
| Root Helm chart and environment values | `infrastructure/helm/urumi`, `values.yaml`, `values-local.yaml`, `values-prod.yaml` |
| Persistent database and store | MySQL with PVC; WordPress + WooCommerce with persistent content; PostgreSQL with PVC for gateway control-plane data |
| Required WooCommerce MCP operations | `get_products`, `get_orders`, `create_order`, `get_customer`; plus product creation, single-order retrieval and order-status update |
| Unified MCP gateway | Single `/mcp` endpoint aggregating WooCommerce, Weather and Currency tools with namespaced tool names |
| Dashboard/control plane | React dashboard and gateway APIs for server status, users/keys, permissions, audit, and chat integration |
| Provider configuration | `LLM_BASE_URL`, `LLM_MODEL` as non-secret Helm values; `LLM_API_KEY` from a Kubernetes Secret |
| Security boundaries | Kubernetes Secret references, API-key authentication, server-side role/tool authorization, upstream timeouts and NetworkPolicies |
| Verification and handoff | Gateway/Woo MCP tests, Helm checks, integration scripts, threat model, runbook, architecture docs, acceptance guide and demo script |
| Source delivery | [`MananBhutada/mcp_gateway_`](https://github.com/MananBhutada/mcp_gateway_) |

## Verification status

The most recent CI run on the original `main` commit identified a real mismatch: gateway tests expected OpenAI-compatible provider settings and bounded tool-call behavior, while the chat implementation still used Anthropic-specific settings. The provider-neutral chat implementation and Helm wiring have been updated on the hardening branch. The new branch's CI must complete before reporting that fix as verified.

Previously recorded local results (22 gateway tests passed with one test deselected, 21 Woo MCP tests passed, Helm tests passed, and dashboard build passed) describe an earlier state and must not be presented as verification of the current branch. Use the workflow result for the exact commit under review.

## Existing demo evidence

The user has already recorded demonstrations of the storefront COD order and admin verification, admin-side order query, Weather/Currency chat, MCP Inspector order listing, API-key revocation, dashboard server status, upstream failure isolation and recovery, and tool visibility when a server is disabled/re-enabled. Preserve those recordings. They establish the flows actually shown; they do not automatically establish clean-install behavior or pod-restart persistence unless those actions appear in the relevant recording.

## Final acceptance gates

1. Confirm the new branch CI passes for gateway tests, Woo MCP tests, dashboard build and local/production Helm validation.
2. Through the gateway `/mcp` endpoint, discover and call `get_products`, `get_orders`, `create_order`, and `get_customer` against disposable data; verify an MCP-created order in WooCommerce.
3. Verify Helm rendering shows the provider URL/model and Secret-backed API key without exposing the key in manifests or Git.
4. Use the recorded live demos for the flows they show; separately run and record any still-required persistence/restart check only if needed and only in the disposable local cluster.

## Security note

Never commit real credentials or put keys, passwords, invitation tokens, or customer personal data in screenshots or video. Local values are disposable development-only values. Production secrets must be injected at deployment time or managed through an approved secret manager.
