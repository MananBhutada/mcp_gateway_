# Urumi AI FDE Internship — Round 1
## MCP Gateway on Kubernetes

Urumi is a Kubernetes-deployed Model Context Protocol (MCP) gateway that presents multiple upstream MCP servers through one authenticated endpoint. This repository contains the implementation, Helm deployment, WooCommerce-backed demo store, dashboard, tests, and assignment handoff documentation.

> **Evidence rule:** source code and automated tests demonstrate implementation; they do not by themselves prove a live Kubernetes checkout or production deployment. See [implementation status](docs/STATUS.md), the [requirement-to-evidence matrix](docs/assessment-gap-matrix.md), and [live acceptance tests](docs/live-acceptance-tests.md).

## Assignment deliverables

- **Helm/Kubernetes:** root chart at `infrastructure/helm/urumi`, shared `values.yaml`, local and production values, workloads, Services, Ingress, Secrets, PVCs, probes, resource controls, and NetworkPolicies.
- **Store:** WordPress + WooCommerce, MySQL-backed persistent data, and a setup Job.
- **MCP gateway:** FastAPI gateway exposing one `/mcp` endpoint and aggregating WooCommerce, Weather, and Currency MCP servers with namespaced tool names.
- **WooCommerce MCP:** candidate implementation for product/order operations via WooCommerce REST; credentials stay in Kubernetes Secrets.
- **Dashboard and control plane:** React/TypeScript UI plus APIs for users, keys, server registry, permissions, audit, and optional tool-calling chat.
- **Security and operations:** role checks, per-user API keys, tool authorization, audit events, upstream timeouts/failure isolation, and network restrictions.
- **Verification material:** CI workflow, unit tests, local integration scripts, Helm validation, threat model, deployment runbook, demo plan, and assessment checklist.

## Architecture

```text
Browser / MCP client
       | one gateway URL + per-user bearer key
       v
Dashboard proxy / Gateway (/mcp, /api)
       | authenticate -> authorize -> route -> audit
       +------------------+------------------+
       v                  v                  v
 WooCommerce MCP       Weather MCP       Currency MCP
       |
 WooCommerce REST API
       v
 WordPress + WooCommerce ---> MySQL + PVC

Gateway control-plane data: PostgreSQL + PVC
Secrets: runtime credentials; never commit real values
```

The gateway is the client-facing trust boundary. Commerce operations go through WooCommerce REST; the gateway must not query the store database directly. Databases and upstream MCP servers should remain cluster-internal.

## Repository map

| Path | Purpose |
|---|---|
| `services/gateway` | FastAPI gateway, MCP endpoint/client, auth/RBAC, admin APIs, routing, audit and chat |
| `services/woo-mcp` | WooCommerce product/order MCP tools and REST client |
| `services/weather-mcp`, `services/currency-mcp` | Additional upstream MCP servers |
| `dashboard` | React + TypeScript + Vite dashboard |
| `infrastructure/helm/urumi` | Single Helm chart and environment values |
| `tests` | Gateway, Woo MCP, Helm-template and local integration checks |
| `docs` | Architecture, system design, threat model, runbook, acceptance evidence and demo guide |

## Local setup

Prerequisites: Docker Desktop, kubectl, Helm 3, k3d, Python 3.12, Node.js 22, and PowerShell or Git Bash/WSL.

From the repository root:

```powershell
helm lint infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
helm template urumi infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
./scripts/dev.sh
kubectl get pods,pvc,ingress,jobs
```

If PowerShell cannot run the shell script, execute it through Git Bash or WSL. Add the local host entries as administrator if your environment requires them:

```text
127.0.0.1 store.urumi.local dashboard.urumi.local
```

Then open `http://store.urumi.local` and `http://dashboard.urumi.local`. Use only disposable local values for the local cluster. The script is intended for development/demo use, not as a production installer.

## Configuration and secrets

- Keep actual API keys, passwords, signing/encryption keys, and populated secret files out of Git.
- `values-local.yaml` is for a disposable local demo only. Rotate any credential that has been exposed outside that environment.
- Use `values-prod.yaml` with unique secrets supplied through an approved secret manager or deployment-time injection.
- Do not expose MySQL, PostgreSQL, or upstream MCP Services through public Ingress.
- Do not put a member key, WooCommerce REST secret, or provider API key in screenshots or the demo recording.

## MCP client

Configure an MCP client to use the gateway URL `http://dashboard.urumi.local/mcp` in the local demo and send `Authorization: Bearer <user-api-key>`. Use a dedicated member key for authorization demonstrations; do not record or publish the key itself.

## Verification commands

```powershell
python -m pip install -r services/gateway/requirements.txt
python -m pip install -r services/woo-mcp/requirements.txt pytest
pytest -q tests/gateway
pytest -q tests/woo_mcp
npm --prefix dashboard ci
npm --prefix dashboard run build
helm lint infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
helm lint infrastructure/helm/urumi -f infrastructure/helm/urumi/values-prod.yaml
helm template urumi infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
helm template urumi infrastructure/helm/urumi -f infrastructure/helm/urumi/values-prod.yaml
```

See [the demo script](docs/demo-script.md) for the suggested recording order and [the runbook](docs/store-deployment-runbook.md) for live-store and persistence gates.

## Known boundaries

- A successful local/unit test is not proof of browser checkout, pod restart persistence, or production-like k3s operation.
- Chat tool-calling requires a valid configured model provider key; dashboard gateway authentication uses a **Urumi Gateway API key**, not the provider key.
- Invitation email delivery is not implemented; invitations are generated by the API/UI flow and shared as a one-time link/token.
- The local chart and app are assignment/demo infrastructure, not a claim of production certification. Follow the status and acceptance documents before marking any live gate complete.

## Assignment handoff

The intended walkthrough is: inspect the chart and trust boundaries, show the running store/dashboard, demonstrate the single gateway endpoint and namespaced tools, prove role/tool permission behavior, show audit records, and explain the persistence/failure-isolation checks. Be explicit about which checks were actually run and which remain pending.
