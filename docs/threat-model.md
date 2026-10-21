# Threat model and security controls

This note describes the threats visible in the current source and Helm templates. The recorded local k3d run demonstrates key revocation, failure isolation, audit attribution, tool permission filtering, and upstream disable.

## A. Shared upstream credentials

**Threat.** A member may use a shared WooCommerce credential indirectly without ever seeing its raw value. A compromised or over-permissioned tool can exercise the upstream privileges available to that credential.

**What the code does.**
- Server credentials supplied through the gateway server-registry API are encrypted before persistence and decrypted only for server-side upstream requests. See `services/gateway/app/auth/api_keys.py` (`encrypt`/`decrypt`), `services/gateway/app/api/admin.py` (`add_server`, `patch_server`, and `_srv`), and `services/gateway/app/routing/router.py` (`refresh_server`, `execute`). The server API returns only `has_credential`, never the credential.
- The upstream MCP client adds that server's configured credential as `Authorization: Bearer ...` only when opening its Streamable HTTP session. See `services/gateway/app/mcp/client.py`. WooCommerce REST credentials are read from environment variables inside the Woo MCP service and used to sign REST requests; they are not returned by the tool handlers. See `services/woo-mcp/app/woocommerce.py`.
- Kubernetes deployment credentials are referenced from `urumi-secrets` in `infrastructure/helm/urumi/templates/secrets.yaml`, `templates/gateway.yaml`, `templates/mcp-servers.yaml`, and `templates/wordpress.yaml`. Kubernetes Secret objects are base64-encoded by the Kubernetes API; encryption at rest depends on cluster configuration and is not established by these templates.
- Tool discovery filters through `tool_allowed` in `services/gateway/app/routing/router.py`; execution checks the same permission again before calling an upstream. Admins can call all tools. For non-admin roles, a matching explicit deny blocks a tool; a missing permission row means allowed. See `services/gateway/app/auth/rbac.py` and `services/gateway/app/models/tables.py`.
- Members can call enabled, reachable upstream tools that their role is permitted to use, including tools that operate with a shared upstream credential. Members cannot retrieve the raw stored server credential through the server API. Admin-only server management endpoints are protected by `require_admin` in `services/gateway/app/api/admin.py`.

**Residual risk.** Permission checks limit which tools a member can invoke; they do not constrain what a permitted tool can do internally beyond that tool's own validation and the privileges of the shared upstream credential. Explicitly deny sensitive tools to members and use least-privilege upstream credentials. Database encryption protects registered server credentials only while the encryption key remains secret. The chart's `values-local.yaml` values are disposable demo credentials, not production secrets.

## B. Why client tokens are not passed through upstream

**Threat.** Forwarding a caller's gateway API key to an upstream would confuse the gateway identity with an upstream identity, leak a client credential to another trust domain, and make authorization/revocation inconsistent.

**What the code does.**
- The bearer token is checked at the gateway by `user_from_token`, which hashes the presented token and looks up its API-key record. See `services/gateway/app/auth/rbac.py` and `services/gateway/app/auth/api_keys.py`.
- Upstream requests use the credential stored for that upstream, not the inbound client's authorization header. The exact upstream header construction is `headers = {"Authorization": f"Bearer {credential}"} if credential else None` in `services/gateway/app/mcp/client.py` within `_run`. The Woo REST client separately signs requests using `WOO_CONSUMER_KEY` and `WOO_CONSUMER_SECRET` in `services/woo-mcp/app/woocommerce.py`.
- User keys are stored as HMAC hashes, shown once at creation, and checked on each gateway request. See `services/gateway/app/auth/api_keys.py`, `services/gateway/app/auth/rbac.py`, and `services/gateway/app/api/admin.py`.
- Audit records include the authenticated user identity, server, tool, source, duration and outcome. See `services/gateway/app/routing/router.py` and `services/gateway/app/models/tables.py`.

**Residual risk.** Revoking a gateway key blocks future requests authenticated with that key at the gateway; it does not revoke a WooCommerce credential at WooCommerce itself. Audit attribution records the gateway user who initiated a call, not a separate upstream identity. Key revocation was verified in the recorded local k3d run; upstream header construction is described in the source references above.

## C. Untrusted upstream MCP servers

**Threats and controls.**

| Threat | What the code does | Residual risk |
|---|---|---|
| Tool description attempts prompt injection/tool poisoning | `services/gateway/app/routing/router.py` exposes upstream descriptions to the model. `services/gateway/app/api/chat.py` uses a server-controlled system instruction that says tool outputs are untrusted and must not be used to reveal secrets. | The instruction is not a sandbox. A model may still be influenced by malicious descriptions or results. Admins must trust and review configured servers. |
| Tool output contains injected instructions or sensitive content | Chat results are treated as untrusted data by the system instruction; tool calls still pass through `R.execute` and its authorization check. | The gateway cannot prove that arbitrary upstream content is truthful or safe. Review tool outputs and avoid granting risky tools unnecessarily. |
| Upstream is slow or dead | `services/gateway/app/config.py` defines `UPSTREAM_TIMEOUT` (default 5 seconds) and `UPSTREAM_CALL_TIMEOUT` (default 30 seconds). `services/gateway/app/mcp/client.py` wraps each short-lived session in a timeout. `refresh_server` catches failures, removes that server's cached tools, and marks it `unreachable`; `refresh_all` isolates refresh failures across servers. | Timeouts do not prevent every resource-exhaustion pattern. Failure isolation was verified in the recorded local k3d run. |
| Two servers register the same tool name | `services/gateway/app/routing/collisions.py` prefixes each tool as `<server>__<tool>`, for example `woocommerce__list_products` and `weather__list_products`. | Namespacing avoids same-name ambiguity but does not make a malicious tool safe. |
| Admin registers an internal URL (SSRF) | `services/gateway/app/api/admin.py` calls `R.validate_url` at registration and URL update. `services/gateway/app/routing/router.py` validates again during health refresh and immediately before execution. It rejects non-HTTP(S), missing hostnames, embedded URL credentials, metadata hostnames `metadata.google.internal`, `metadata`, and `instance-data`, plus IP literals that are link-local, multicast, unspecified, or reserved. | **Private and cluster IPs are intentionally allowed** for in-cluster MCP Services. **Loopback is not explicitly blocked**: `ipaddress.is_loopback` is not checked, so loopback IP literals are not rejected by this function alone. Ordinary private RFC1918 addresses are also not rejected. Hostname resolution/rebinding and redirects need additional review; upstream MCP client behavior is not an operator-managed hostname allowlist. |
| Upstream reaches other cluster services | `infrastructure/helm/urumi/templates/networkpolicy.yaml` defines default-deny ingress, per-workload ingress allowances, selected egress allowances, and explicit empty egress rules for MySQL and PostgreSQL. | NetworkPolicies are a second layer, not a substitute for URL validation. Actual enforcement depends on the cluster network plugin and the rendered/live policy state. Gateway egress includes TCP/443 without a destination selector, so it is not a strict destination allowlist. |
| Tool call succeeds or fails without attribution | `R.execute` records an audit event for successful results and exception/error paths through `audit.record`; the audit model records user, server, tool, source, duration, success and error. | Audit attribution was verified in the recorded local k3d run. Audit persistence during database failure is not guaranteed. Admin-only audit API visibility is enforced by `require_admin`. |

**SSRF boundary, explicitly.** The validator blocks the listed metadata names and IP literals that are link-local, multicast, unspecified, or reserved. It does **not** block private IP literals, cluster DNS names, or loopback IP literals. These allowances support in-cluster MCP endpoints but mean that a privileged admin can register some internal targets. The NetworkPolicies in `infrastructure/helm/urumi/templates/networkpolicy.yaml` are the additional network boundary.

## D. What one team member can do to another

**Threat.** A member may attempt to read another user's key, inspect their audit history, access another user's chat history, revoke their key, or impersonate their identity.

**What the code does.**
- Each API key belongs to a user, is stored as a hash, and can be marked revoked. `services/gateway/app/models/tables.py` defines `ApiKey.user_id`, `key_hash`, and `revoked`; `services/gateway/app/auth/rbac.py` rejects unknown or revoked keys.
- The current API has `POST /api/me/keys` to create a key for the authenticated user and `POST /api/users/{uid}/keys` for an admin to create a key for a specified user. The raw key is returned once by the creation response. `GET /api/users`, `POST /api/keys/{kid}/revoke`, `GET /api/audit`, server management, invitations, and tool-permission management require `require_admin`. See `services/gateway/app/api/admin.py`.
- A member cannot use the admin-only endpoints to list users/keys, view audit rows, revoke another user's key, manage upstream servers, or change role permissions. The `/api/me` response exposes only the authenticated user's ID, email, name and role.
- The gateway chat endpoint accepts the current user's messages in the request and executes tools under that authenticated user. See `services/gateway/app/api/chat.py`. No persisted chat-history API or cross-user chat-history table is defined in the inspected `services/gateway/app/models/tables.py`.
- The audit record captures the user email associated with each tool call. See `services/gateway/app/routing/router.py` and `services/gateway/app/models/tables.py`.
- Any authenticated member can call `GET /api/servers` and `GET /api/tools`. `GET /api/servers` returns each upstream's name, URL, status, `last_error`, and `has_credential`; it never returns the credential.

**Residual risk.** The current revoke endpoint is admin-only; the code does not provide a member self-revoke endpoint. A member can create additional keys for their own account through `/api/me/keys`. Admins can create keys for other users and revoke any key. No chat-history persistence is present in the inspected model, but browser-side storage behavior is outside these files. Tool permission filtering and upstream disable were verified in the recorded local k3d run.

**Known residual exposure.** The member-accessible server and tool endpoints expose internal upstream URLs and error text to authenticated members. The `has_credential` field reveals only whether a credential is configured, never its value.

## Other controls

| Control | Source evidence | Boundary |
|---|---|---|
| Non-root gateway and MCP containers | `templates/gateway.yaml` and `templates/mcp-servers.yaml` set `runAsNonRoot: true`, UID 10001, and disable privilege escalation. | WordPress, dashboard, database, and setup Job have different security contexts; do not generalize the same setting to every container. |
| Default-deny NetworkPolicies | `templates/networkpolicy.yaml` creates `default-deny-ingress` and specific ingress rules. | Egress is controlled per workload; not every workload has a universal deny-all policy. |
| Credentials referenced from Kubernetes Secrets | `templates/secrets.yaml` defines `urumi-secrets`; workload templates reference keys from it. | The chart alone does not configure Kubernetes Secret encryption at rest or an external secret manager. |
| Database egress denied | `templates/networkpolicy.yaml` creates `deny-egress-mysql` and `deny-egress-postgres` with empty egress rules. | NetworkPolicy enforcement depends on the cluster network plugin. |
| Persistent volumes | `templates/pvc.yaml` defines MySQL, WordPress and PostgreSQL PVCs. | PVCs are not backups. |

## Known limitations

- `infrastructure/helm/urumi/values-local.yaml` contains disposable demo credentials and an empty `llmApiKey`; do not reuse it in production.
- The chart uses Kubernetes Secret objects but does not configure etcd encryption at rest or an external secret manager.
- `services/gateway/app/routing/router.py` keeps `TOOL_CACHE` in process memory. Two gateway replicas have independent caches; no shared invalidation mechanism is defined here.
- `values-local.yaml` configures HTTP hosts and does not set an Ingress TLS Secret. TLS/cert-manager is not configured by the local values.
- The SSRF validator intentionally allows private and cluster IPs and does not explicitly block loopback IP literals.
- The gateway does not implement HTTP-level rate limits.
