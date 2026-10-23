# Urumi AI FDE Internship — Round 1
## MCP Gateway on Kubernetes

Urumi is a Kubernetes-deployed Model Context Protocol (MCP) gateway that presents multiple upstream MCP servers through one authenticated endpoint. This repository contains the Helm deployment, WordPress + WooCommerce demo store, gateway, dashboard, three upstream MCP servers, tests, and submission documentation.

## Contents

- [Assignment deliverables](#assignment-deliverables)
- [Architecture](#architecture)
- [Repository map](#repository-map)
- [Local setup](#local-setup)
- [Configuration and secrets](#configuration-and-secrets)
- [Production / VPS (k3s) setup](#production--vps-k3s-setup)
- [Place an order](#place-an-order)
- [Connect an external MCP client](#connect-an-external-mcp-client)
- [Use the chat agent](#use-the-chat-agent)
- [Definition-of-done walkthrough](#definition-of-done-walkthrough)
- [Bonus and stand-out items](#bonus-and-stand-out-items)
- [System design and threat model](#system-design-and-threat-model)
- [Documentation](#documentation)
- [Verification commands](#verification-commands)
- [Known limitations](#known-limitations)
- [Submission summary](#submission-summary)
- [Demo video](#demo-video)

## Assignment deliverables

- **Helm/Kubernetes:** root chart at `infrastructure/helm/urumi`, shared `values.yaml`, local and production values, workloads, Services, Ingress, Secrets, PVCs, probes, resource controls, and NetworkPolicies.
- **Store:** WordPress + WooCommerce, MySQL-backed persistent data, and a setup Job.
- **MCP gateway:** FastAPI gateway exposing one `/mcp` endpoint and aggregating WooCommerce, Weather, and Currency MCP servers with namespaced tool names.
- **WooCommerce MCP:** REST-backed product, order, and customer operations.
- **Dashboard/control plane:** React/TypeScript UI and APIs for users, API keys, server registry, tool permissions, audit, and chat.
- **Security and operations:** authentication, role/tool authorization, audit events, upstream timeouts and failure isolation, and NetworkPolicies.
- **Submission evidence:** recorded local k3d walkthrough, tests, Helm validation, system design, threat model, deployment runbook, acceptance record, and demo script.

## Architecture

```text
Browser / external MCP client
       | gateway URL + per-user bearer key
       v
Dashboard / Gateway (/mcp, /api)
       | authenticate -> authorize -> route -> audit
       +------------------+------------------+
       v                  v                  v
 WooCommerce MCP       Weather MCP       Currency MCP
       |
 WooCommerce REST API
       v
 WordPress + WooCommerce ---> MySQL + PVC

Gateway control-plane data: PostgreSQL + PVC
Credentials: Kubernetes Secrets and server-side credential handling
```

<p align="center">
  <img width="100%" alt="Urumi architecture: Team MCP Gateway and WooCommerce on Kubernetes" src="https://github.com/user-attachments/assets/7f73a208-0da1-458e-b2bd-c3ecf393372c" />
</p>

The gateway is the client-facing trust boundary. Commerce operations use the WooCommerce REST API; the gateway does not query the store database directly. The connected upstream servers are WooCommerce (written in-house), Weather, and Currency.

## Repository map

| Path | Purpose |
|---|---|
| `services/gateway` | FastAPI gateway, MCP endpoint/client, auth/RBAC, admin APIs, routing, audit, and chat |
| `services/woo-mcp` | WooCommerce product/order/customer MCP tools and REST client |
| `services/weather-mcp`, `services/currency-mcp` | Weather and Currency upstream MCP servers |
| `dashboard` | React + TypeScript + Vite dashboard |
| `infrastructure/helm/urumi` | Root Helm chart and environment values |
| `tests` | Gateway, Woo MCP, Helm-template, and integration tests |
| `docs` | Architecture, system design, threat model, runbooks, evidence matrix, and demo guide |

## Local setup

Prerequisites: Docker Desktop, `kubectl`, Helm 3, `k3d`, Python 3.12, Node.js 22, and PowerShell or Git Bash/WSL.

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

Open `http://store.urumi.local` and `http://dashboard.urumi.local`. These local hostnames resolve to the local machine when configured this way. This is a local k3d deployment, not a publicly reachable VPS.

## Configuration and secrets

- Keep real API keys, passwords, signing/encryption keys, and populated secret files out of Git.
- The LLM provider URL and model use `llm.baseUrl` and `llm.model`. The provider key uses `secrets.llmApiKey` and is injected into the gateway as `LLM_API_KEY`.
- The chat endpoint calls an OpenAI-compatible `/chat/completions` endpoint. Local values default to `https://openrouter.ai/api/v1` and `openrouter/free`; `secrets.llmApiKey` is empty by default.
- Production uses `infrastructure/helm/urumi/values-prod.yaml` with deploy-time `--set-string` overrides or an approved secret manager. No production secret exists in the repository.
- Do not expose MySQL, PostgreSQL, or upstream MCP Services through public Ingress.
- Kubernetes Secret objects are used for deployment credentials; the chart does not configure Kubernetes Secret encryption at rest or install an external secret manager.
- Do not put API keys, passwords, invitation tokens, or customer personal data in screenshots or the demo recording.

### Local demo credentials

The values in `infrastructure/helm/urumi/values-local.yaml` are throwaway, local-only values for a disposable k3d cluster reachable only through local hostnames. They grant nothing outside that cluster. They are committed so `./scripts/dev.sh` runs with zero setup. Never reuse them in another environment. Production uses `values-prod.yaml` plus deploy-time `--set-string` overrides in the [production install command](#supply-secrets-and-install); no production secret exists in the repository.

## Production / VPS (k3s) setup

The production path uses the same Helm chart as the local deployment, with `infrastructure/helm/urumi/values-prod.yaml` and deployment-specific hosts, image references, and secrets. This is the documented, chart-identical production path; no specific VPS provisioning is represented here.

### Prerequisites

- A Linux VPS with a supported Linux distribution, a public IP address, and SSH access.
- A DNS zone where you can create A records.
- Docker/build tooling on the build machine, a container registry accessible by the VPS, and `kubectl`/Helm.
- Unique production credentials for MySQL, PostgreSQL, gateway signing, bootstrap admin, WordPress admin, WooCommerce REST, Woo MCP authentication, and the selected LLM provider.

### Install k3s and configure DNS

On the VPS, install k3s using the official installer:

```bash
curl -sfL https://get.k3s.io | sh -
```

Configure `kubectl` access securely from the administration machine according to the k3s documentation; do not publish the cluster admin kubeconfig. Create DNS A records pointing both `store.YOURDOMAIN.com` and `app.YOURDOMAIN.com` to the VPS public IP. Replace those placeholders in `infrastructure/helm/urumi/values-prod.yaml`.

The chart defaults to the `traefik` Ingress class. The k3s cluster needs a matching Ingress controller enabled and reachable.

### Build and push images

Build each image from its own build context, tag it with a version, and push it to a registry the VPS can pull from. Replace registry, account, and version values in this example:

```bash
docker build -t ghcr.io/YOURUSER/urumi-gateway:0.1.0 -f services/gateway/Dockerfile services/gateway
docker build -t ghcr.io/YOURUSER/urumi-dashboard:0.1.0 -f dashboard/Dockerfile dashboard
docker build -t ghcr.io/YOURUSER/urumi-woo-mcp:0.1.0 -f services/woo-mcp/Dockerfile services/woo-mcp
docker build -t ghcr.io/YOURUSER/urumi-weather-mcp:0.1.0 -f services/weather-mcp/Dockerfile services/weather-mcp
docker build -t ghcr.io/YOURUSER/urumi-currency-mcp:0.1.0 -f services/currency-mcp/Dockerfile services/currency-mcp

docker push ghcr.io/YOURUSER/urumi-gateway:0.1.0
docker push ghcr.io/YOURUSER/urumi-dashboard:0.1.0
docker push ghcr.io/YOURUSER/urumi-woo-mcp:0.1.0
docker push ghcr.io/YOURUSER/urumi-weather-mcp:0.1.0
docker push ghcr.io/YOURUSER/urumi-currency-mcp:0.1.0
```

Update `images.gateway`, `images.dashboard`, `images.wooMcp`, `images.weatherMcp`, and `images.currencyMcp` in `values-prod.yaml` to match the pushed image references and tags. For a private registry, configure image-pull credentials separately; the chart does not define an `imagePullSecret`.

### Supply secrets and install

The chart's `infrastructure/helm/urumi/templates/secrets.yaml` supports `secrets.mysqlRootPassword`, `secrets.mysqlPassword`, `secrets.postgresPassword`, `secrets.gatewaySecretKey`, `secrets.bootstrapAdminKey`, `secrets.wpAdminPassword`, `secrets.wooConsumerKey`, `secrets.wooConsumerSecret`, `secrets.wooMcpToken`, and `secrets.llmApiKey`. Supply unique values through a protected deployment environment or a private values file excluded from Git. Avoid putting secrets directly in shell history.

After exporting the variables securely in the deployment environment:

```bash
helm upgrade --install urumi infrastructure/helm/urumi \
  -f infrastructure/helm/urumi/values.yaml \
  -f infrastructure/helm/urumi/values-prod.yaml \
  --set-string secrets.gatewaySecretKey="$GATEWAY_SECRET_KEY" \
  --set-string secrets.bootstrapAdminKey="$BOOTSTRAP_ADMIN_KEY" \
  --set-string secrets.mysqlRootPassword="$MYSQL_ROOT_PASSWORD" \
  --set-string secrets.mysqlPassword="$MYSQL_PASSWORD" \
  --set-string secrets.postgresPassword="$POSTGRES_PASSWORD" \
  --set-string secrets.wpAdminPassword="$WP_ADMIN_PASSWORD" \
  --set-string secrets.wooConsumerKey="$WOO_CONSUMER_KEY" \
  --set-string secrets.wooConsumerSecret="$WOO_CONSUMER_SECRET" \
  --set-string secrets.wooMcpToken="$WOO_MCP_TOKEN" \
  --set-string secrets.llmApiKey="$LLM_API_KEY"
```

The command applies shared values first and production values second. The production values reference a TLS Secret named `urumi-tls`; create and validate that Secret before relying on HTTPS. The chart does not install cert-manager or issue a certificate.

### Post-install checks

```bash
kubectl get pods -o wide
kubectl get pvc
kubectl get ingress
kubectl get jobs
kubectl get services
```

Check that workloads are Ready, PVCs are Bound, the WordPress setup Job completed, and Ingress hosts match DNS. Open `https://store.YOURDOMAIN.com` and `https://app.YOURDOMAIN.com` after DNS, ingress routing, and the `urumi-tls` Secret are configured. The production configuration uses the same chart templates as the local configuration.

## Place an order

1. Open `http://store.urumi.local` in the local demo (or the configured production storefront URL).
2. Open a published product and select **Add to cart**.
3. Open the cart and continue to checkout.
4. Enter disposable test customer details and select **Cash on delivery (COD)**.
5. Place the order and note the order number.
6. Open WordPress admin at `http://store.urumi.local/wp-admin` (or `https://store.YOURDOMAIN.com/wp-admin` in a configured production deployment).
7. Sign in with the WordPress admin username `admin` and the password supplied as `secrets.wpAdminPassword` to the Helm chart, stored in Kubernetes Secret key `wp-admin-password` in `urumi-secrets`.
8. Open **WooCommerce → Orders** in wp-admin and confirm the order number, line items, total, payment method, and status.

Use test data only. The recorded local k3d walkthrough demonstrates storefront COD checkout, order visibility in WooCommerce admin, and order persistence after a pod restart.

## Connect an external MCP client

The local gateway MCP endpoint is `http://dashboard.urumi.local/mcp`; the dashboard's same-origin proxy forwards MCP requests to the gateway. For production, use the configured HTTPS dashboard host and `/mcp`. Each request includes `Authorization: Bearer <user-api-key>`. This is a Urumi gateway API key, not the LLM provider key.

### Create a member key

An admin creates a member account or invitation through the dashboard's user/invitation workflow. A member can create another key for their own account through the dashboard key workflow, backed by `POST /api/me/keys`. The raw key is returned once; copy it into the MCP client's secret configuration and do not commit it.

### MCP Inspector

Open MCP Inspector, choose an HTTP/Streamable HTTP connection, set the URL to `http://dashboard.urumi.local/mcp`, and add this header:

```text
Authorization: Bearer <user-api-key>
```

Initialize the connection, list tools, and run a harmless read operation.

### Claude Code

```bash
claude mcp add --transport http urumi http://dashboard.urumi.local/mcp --header "Authorization: Bearer <user-api-key>"
```

Use the production HTTPS host instead of the local URL for a remote deployment.

### Cursor

Add an MCP server entry to Cursor's MCP configuration (`mcp.json`):

```json
{
  "mcpServers": {
    "urumi": {
      "url": "http://dashboard.urumi.local/mcp",
      "headers": {
        "Authorization": "Bearer <user-api-key>"
      }
    }
  }
}
```

Replace the local URL for production and replace the placeholder with a real member key. Do not commit a populated configuration containing the key.

The recorded local k3d walkthrough demonstrates that user B connects with only the gateway URL and B's API key, sees tools from every enabled upstream, answers the orders question, and runs a prompt that calls two upstream servers.

## Use the chat agent

1. Open `http://dashboard.urumi.local` and sign in with a **Urumi Gateway API key**.
2. Open the dashboard's chat/agent area. The chat API route is `POST /api/chat`.
3. Configure `llm.baseUrl`, `llm.model`, and `secrets.llmApiKey` in Helm values. The gateway reads these as `LLM_BASE_URL`, `LLM_MODEL`, and `LLM_API_KEY` and calls an OpenAI-compatible `/chat/completions` endpoint. Local values use `https://openrouter.ai/api/v1` and `openrouter/free`; `secrets.llmApiKey` is empty by default and must be supplied for live provider calls.
4. Try prompts such as:
   - Create a simple product named Demo Mug for 299.00 and publish it so it appears in the storefront.
   - What orders came in today? Summarize order IDs, statuses, totals, and payment methods.
   - Example cross-server prompt: "Total today's orders and convert that total to EUR." This uses WooCommerce to retrieve orders and Currency to convert the total.
5. The chat response includes `tool_trace` entries for tool calls and errors. Tool calls execute through the gateway router under the logged-in user's identity and permissions, and audit events record that user.

The recorded local k3d walkthrough demonstrates that user A publishes a product through chat, sees it on the storefront, and asks about the manually placed order with tool calls shown in the trace.

## Definition-of-done walkthrough

All steps below were completed in the recorded local k3d run using `infrastructure/helm/urumi` and `values-local.yaml`.

| Step | Action (UI or exact command) | Expected result | Status |
|---|---|---|---|
| Store checkout | Open `http://store.urumi.local`, add a product to cart, complete checkout with COD, then open WooCommerce → Orders in wp-admin. | The order appears in WooCommerce admin with its order details. | Verified, local k3d run |
| Persistence | Restart WordPress with `kubectl rollout restart deployment/wordpress`; wait with `kubectl rollout status deployment/wordpress`, then recheck the order in wp-admin. | The existing order remains after pod restart. | Verified, local k3d run |
| User A chat product | In the dashboard chat agent, ask it to create a named product with a price and publish it. | The product is published and appears on the storefront; tool calls appear in the trace. | Verified, local k3d run |
| User A orders question | After the manual storefront order, ask user A's chat agent: "What orders came in today?" | The response identifies the order; the trace shows the tool calls. | Verified, local k3d run |
| User B external MCP client | Configure an external MCP client with `http://dashboard.urumi.local/mcp` and user B's API key only. Ask: "What orders came in today?" | The client connects, discovers tools from every enabled server, and answers the orders question. | Verified, local k3d run |
| Two-upstream prompt | In the chat agent, use the example prompt: "Total today's orders and convert that total to EUR." | The trace shows WooCommerce order retrieval and a Currency conversion call. | Verified, local k3d run |
| Tool permissions | In the dashboard Team/permissions workflow, grant or deny a MEMBER tool permission, then refresh the member's tool list and try a denied direct call. | Tool discovery and execution follow the configured member permission. | Verified, local k3d run |
| Disable an upstream | In the dashboard server registry, disable one upstream; refresh the chat agent and external MCP client tool lists. | The disabled server's tools disappear from both clients; other enabled servers remain available. | Verified, local k3d run |
| Revoke user B key | In the admin key-management workflow, revoke B's key; send another request from B's external client. | B's next request is rejected. | Verified, local k3d run |
| Upstream pod failure | Run `kubectl delete pod -l app=weather-mcp`, then watch replacement with `kubectl get pods -w`. | The Weather pod is replaced; the other upstream servers continue working and the dashboard shows the failed upstream as unreachable during failure. | Verified, local k3d run |
| Audit attribution | Make tool calls as users A and B, then inspect the dashboard audit view. | Each call appears in the audit log with the correct user attribution. | Verified, local k3d run |

The screen-recorded demo is the evidence artifact for this walkthrough. The three connected upstreams are WooCommerce (written in-house), Weather, and Currency.

## Bonus and stand-out items

- **Role-based tool permissions at discovery and execution:** `services/gateway/app/auth/rbac.py`, `services/gateway/app/routing/router.py`, `services/gateway/app/api/admin.py`.
- **Encrypted upstream credential storage:** `services/gateway/app/auth/api_keys.py`, `services/gateway/app/api/admin.py`, `services/gateway/app/routing/router.py`.
- **SSRF URL validation at registration, health refresh, and execution:** `services/gateway/app/api/admin.py`, `services/gateway/app/routing/router.py`.
- **Default-deny ingress and scoped NetworkPolicies, including database egress denial:** `infrastructure/helm/urumi/templates/networkpolicy.yaml`.
- **Non-root gateway and MCP containers:** `infrastructure/helm/urumi/templates/gateway.yaml`, `infrastructure/helm/urumi/templates/mcp-servers.yaml`.
- **Two-replica production gateway setting:** `infrastructure/helm/urumi/values-prod.yaml`; the tool cache is per replica and cache coordination is not implemented.

## System design and threat model

The gateway authenticates each client request, filters tool discovery by role/tool permissions, checks permissions again at execution, routes namespaced calls to upstream MCP servers, and records audit events. WooCommerce operations use the WooCommerce REST API. The production configuration reuses the same Helm chart with environment-specific values.

See [System design](docs/system-design.md) for routing, timeouts, failure handling, scaling trade-offs, and Helm operations. See [Threat model](docs/threat-model.md) for shared credentials, client-key boundaries, SSRF controls, NetworkPolicies, and residual exposure of upstream metadata.

## Documentation

- [Architecture](docs/architecture.md)
- [MCP request flow](docs/mcp-flow.md)
- [Implementation status](docs/STATUS.md)
- [Requirement-to-evidence matrix](docs/assessment-gap-matrix.md)
- [Acceptance evidence record](docs/live-acceptance-tests.md)
- [Store deployment runbook](docs/store-deployment-runbook.md)
- [Demo script](docs/demo-script.md)
- [Implementation checklist](docs/implementation-checklist.md)

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

## Known limitations

- The chart does not install cert-manager or issue TLS certificates; production values reference the `urumi-tls` Secret.
- `services/gateway/app/routing/router.py` keeps `TOOL_CACHE` in process memory. Gateway replicas have independent caches and no shared invalidation mechanism.
- Kubernetes Secret encryption at rest is not configured by the chart.
- The SSRF validator does not block loopback IP literals. Private and cluster IPs are allowed for in-cluster MCP endpoints.
- The gateway does not implement HTTP-level rate limits.
- PVCs preserve data across pod replacement but are not backups.

## Submission summary

Delivered: the root Helm chart and local/production values, WordPress + WooCommerce store, gateway, dashboard, WooCommerce/Weather/Currency upstreams, tests, and documentation. Demonstrated in the recorded local k3d run: COD checkout and persistence, chat-based product creation and order lookup, external MCP access with user B's key, cross-upstream tool use, tool permissions, upstream disable and failure isolation, key revocation, and audit attribution. The evidence record is in [Requirement-to-evidence matrix](docs/assessment-gap-matrix.md), [Implementation status](docs/STATUS.md), and [Acceptance evidence record](docs/live-acceptance-tests.md).

## Demo video
https://drive.google.com/drive/folders/1kRacyk5BwoXWgxJG3Sg_4-HCET0bPm_k
