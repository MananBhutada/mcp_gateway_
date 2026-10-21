# Threat model and security controls

This document identifies key risks, intended controls and evidence needed before calling a control verified. A rendered manifest or source file alone does not prove the control is effective in a running cluster.

| Threat | Control / implementation intent | Required verification / residual risk |
|---|---|---|
| Stolen user API key | Keys are intended to be shown once and stored hashed | Create, use, revoke, and retry a disposable key; confirm the revoked key fails |
| Upstream credential disclosure | Runtime Kubernetes Secrets and credential redaction | Scan tracked files and Git history; inspect logs/errors; rotate any exposed credential |
| Member performs admin action | Backend role checks on admin APIs | Test sensitive endpoints with a member key; UI hiding is not sufficient |
| Member invokes a denied tool | Permission filtering during discovery and authorization again at execution | Verify denied tool is hidden and direct tools/call is rejected |
| Malicious server URL / SSRF | Validate registered URLs and constrain network egress | Verify URL validation and NetworkPolicies; DNS rebinding and in-cluster targets need deployment-specific review |
| Lateral movement | Internal Services and Kubernetes NetworkPolicies | Inspect rendered and live policies and test permitted/blocked connectivity |
| Upstream outage or slowness | Bounded timeouts and isolated upstream errors | Disable one upstream and verify healthy upstreams remain usable |
| Revoked key reused | Authentication on each request | Revoke a disposable key and immediately retry via an MCP client |
| Prompt injection in tool output | Treat tool results as untrusted data and route calls through gateway authorization | Add adversarial-output tests; require confirmation for destructive actions |
| Pod/database data loss | PVCs for store and control-plane databases | Restart pods without deleting PVCs; separately plan and test backups/restore |
| Secret or customer data in video/docs | Demo guidance forbids credentials and unnecessary personal data | Review recording and repository before submission |

## Deployment requirements

- Public Ingress should be limited to intended dashboard and storefront hosts.
- MySQL, PostgreSQL and upstream MCP servers should not have public Ingress.
- Production should use TLS, unique high-entropy secrets, least-privilege WooCommerce REST keys and restricted egress.
- Weak/default secrets must not be used in production.
- Logs and errors must not reveal API keys, consumer secrets, raw upstream response bodies or unnecessary customer information.

## Security validation before submission

1. Scan tracked files for credentials; review relevant Git history before making the repository public.
2. Run Helm lint/template with both local and production values and inspect Secrets, Ingress and NetworkPolicies.
3. Verify admin/member authorization and direct tool permission enforcement.
4. Verify key revocation and attributable audit records.
5. Simulate an upstream failure and confirm other servers remain available.
6. Do not claim production security certification from a local assignment demo.
