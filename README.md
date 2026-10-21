# Urumi AI FDE Internship — Round 1
## MCP Gateway on Kubernetes

Urumi is a Kubernetes-deployed Model Context Protocol (MCP) gateway that presents multiple upstream MCP servers through one authenticated endpoint. This repository contains the implementation, Helm deployment, WooCommerce-backed demo store, dashboard, tests, and assignment handoff documentation.

## Assignment deliverables

- **Helm/Kubernetes:** root chart at infrastructure/helm/urumi, shared values.yaml, local and production values, workloads, Services, Ingress, Secrets, PVCs, probes, resource controls, and NetworkPolicies.
- **Store:** WordPress + WooCommerce, MySQL-backed persistent data, and a setup Job.
- **MCP gateway:** FastAPI gateway exposing one /mcp endpoint and aggregating WooCommerce, Weather, and Currency MCP servers with namespaced tool names.
- **WooCommerce MCP:** REST-backed product/order/customer operations. The registered tool names are listed below.
- **Dashboard and control plane:** React/TypeScript UI plus APIs for users, keys, server registry, permissions, audit, and optional tool-calling chat.
- **Security and operations:** role checks, per-user API keys, tool authorization, audit events, upstream timeouts/failure isolation, and network restrictions.
- **Verification material:** CI workflow, unit tests, local integration scripts, Helm validation, threat model, deployment runbook, demo plan, and acceptance checklist.

## WooCommerce MCP tools

The service registers these tools in services/woo-mcp/app/tools/products.py, orders.py, and customers.py. The gateway prefixes names with the upstream server name, so the client sees names such as woocommerce__list_products.

| Tool | Behavior |
|---|---|
| list_products | Canonical product-list tool; returns a minimized product projection and supports per_page and search. |
| get_products | Alias of list_products; same catalog operation and arguments. |
| create_product | Creates a simple product. status defaults to draft; use status="publish" for a product to appear on the storefront. |
| list_orders | Canonical order-list tool; supports after, status, and per_page, and minimizes customer details. |
| get_orders | Alias of list_orders; same order-list operation and arguments. |
| create_order | Creates a pending, unpaid WooCommerce order from product IDs and positive quantities. The demo tool accepts payment_method="cod" and defaults to Cash on Delivery. |
| get_order | Retrieves one order by positive numeric ID. |
| update_order_status | Updates an order to one of the supported WooCommerce statuses. |
| get_customer | Retrieves a customer by numeric ID and returns a minimized profile. |

The tool implementations call the WooCommerce REST API; they do not perform commerce operations by querying MySQL directly. The upstream REST credentials remain within the Woo MCP service.

## Architecture

~~~~text
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
~~~~

The gateway is the client-facing trust boundary. Commerce operations go through WooCommerce REST; the gateway must not query the store database directly. Databases and upstream MCP servers should remain cluster-internal.

## Repository map

| Path | Purpose |
|---|---|
| services/gateway | FastAPI gateway, MCP endpoint/client, auth/RBAC, admin APIs, routing, audit and chat |
| services/woo-mcp | WooCommerce product/order/customer MCP tools and REST client |
| services/weather-mcp, services/currency-mcp | Additional upstream MCP servers |
| dashboard | React + TypeScript + Vite dashboard |
| infrastructure/helm/urumi | Single Helm chart and environment values |
| tests | Gateway, Woo MCP, Helm-template and local integration checks |
| docs | Architecture, system design, threat model, runbook, acceptance evidence and demo guide |

## Local setup

Prerequisites: Docker Desktop, kubectl, Helm 3, k3d, Python 3.12, Node.js 22, and PowerShell or Git Bash/WSL.

From the repository root:

~~~~powershell
helm lint infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
helm template urumi infrastructure/helm/urumi -f infrastructure/helm/urumi/values-local.yaml
./scripts/dev.sh
kubectl get pods,pvc,ingress,jobs
~~~~

If PowerShell cannot run the shell script, execute it through Git Bash or WSL. Add the local host entries as administrator if your environment requires them:

~~~~text
127.0.0.1 store.urumi.local dashboard.urumi.local
~~~~

Then open http://store.urumi.local and http://dashboard.urumi.local. These hostnames resolve to the local machine when configured this way; this is a local Kubernetes deployment, not a publicly reachable VPS deployment. Use only disposable local values for the local cluster. The script is for development/demo use, not a production installer.

## Configuration and secrets

- Keep actual API keys, passwords, signing/encryption keys, and populated secret files out of Git.
- values-local.yaml contains disposable local-demo values; never reuse them in another environment. The llmApiKey is empty by default.
- The LLM provider URL and model are configured as llm.baseUrl and llm.model; the provider key is secrets.llmApiKey and is injected into the gateway as LLM_API_KEY.
- values-prod.yaml contains placeholder hosts and image paths. Replace them and provide unique secrets at deployment time or through an approved secret manager.
- Do not expose MySQL, PostgreSQL, or upstream MCP Services through public Ingress.
- The chart references Kubernetes Secret objects; it does not configure etcd encryption at rest or install an external secret manager.
- Do not put a member key, WooCommerce REST secret, or provider API key in screenshots or the demo recording.

## Production / VPS (k3s) setup

This is a deployment procedure, not evidence that a VPS has already been provisioned.

### Prerequisites

- A Linux VPS with a supported Linux distribution, a public IP address, and SSH access.
- A DNS zone where you can create A records.
- Docker/build tooling on the build machine, a container registry accessible by the VPS, and kubectl/Helm.
- Unique production credentials for MySQL, PostgreSQL, gateway signing, bootstrap admin, WordPress admin, WooCommerce REST, Woo MCP authentication, and the selected LLM provider.

### Install k3s and configure DNS

On the VPS, install k3s using the official installer:

~~~~sh
curl -sfL https://get.k3s.io | sh -
~~~~

Configure kubectl access securely from the administration machine according to the k3s documentation; do not publish the cluster admin kubeconfig. Create DNS A records pointing both store.YOURDOMAIN.com and app.YOURDOMAIN.com to the VPS public IP. Replace those placeholders in infrastructure/helm/urumi/values-prod.yaml.

The chart defaults to the traefik Ingress class. Confirm the k3s installation has the matching Ingress controller enabled and reachable.

### Build and push images

Build each image from its own build context, tag it with a version, and push it to a registry the VPS can pull from. Example pattern (replace registry, account, and version values):

~~~~sh
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
~~~~

TODO(verify): confirm all five Dockerfile paths/build contexts exist in the submitted commit. Update images.gateway, images.dashboard, images.wooMcp, images.weatherMcp, and images.currencyMcp in values-prod.yaml to match the pushed image references and tags. If the registry is private, configure image-pull credentials separately; this chart does not define an imagePullSecret.

### Supply secrets and install

The chart's templates/secrets.yaml supports these values: secrets.mysqlRootPassword, secrets.mysqlPassword, secrets.postgresPassword, secrets.gatewaySecretKey, secrets.bootstrapAdminKey, secrets.wpAdminPassword, secrets.wooConsumerKey, secrets.wooConsumerSecret, secrets.wooMcpToken, and secrets.llmApiKey. Supply unique values through a protected deployment environment or a private values file excluded from Git. Avoid putting secrets directly in shell history.

For example, after exporting the variables securely in the deployment environment:

~~~~sh
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
~~~~

The command uses the shared values first and production values second, so production values override shared defaults. The values-prod.yaml file currently references a TLS Secret named urumi-tls; create and validate that Secret before relying on HTTPS. The repository does not configure cert-manager or issue a certificate automatically.

### Post-install verification

~~~~sh
kubectl get pods -o wide
kubectl get pvc
kubectl get ingress
kubectl get jobs
kubectl get services
~~~~

Verify that workloads are Ready, PVCs are Bound, the WordPress setup Job completed, and Ingress hosts match the DNS records. Then open https://store.YOURDOMAIN.com and https://app.YOURDOMAIN.com only after DNS, ingress routing and the urumi-tls Secret are configured. Verify WooCommerce checkout, gateway MCP discovery/calls, permissions, audit records, and restart persistence. Mark each live check complete only after observing it.

## How to place an order

1. Open http://store.urumi.local in the local demo (or the configured production storefront URL).
2. Open a published product and select **Add to cart**.
3. Open the cart and continue to checkout.
4. Enter disposable test customer details and select **Cash on delivery (COD)** as the payment method.
5. Place the order and note the order number.
6. Open the WordPress admin at http://store.urumi.local/wp-admin (or https://store.YOURDOMAIN.com/wp-admin in a configured production deployment).
7. Sign in with the WordPress admin username admin and the password supplied as secrets.wpAdminPassword to the Helm chart, stored in Kubernetes Secret key wp-admin-password in urumi-secrets.
8. In wp-admin, open **WooCommerce → Orders** and find the order number. Confirm line items, total, payment method and status.

Use test data only. Do not place real customer details or credentials in a recording.

## How to connect an external MCP client

The gateway MCP endpoint is http://dashboard.urumi.local/mcp in the local demo; the dashboard's same-origin proxy forwards MCP requests to the gateway. For production, use the configured HTTPS dashboard host and /mcp. Each request must include Authorization: Bearer <user-api-key>. The key is a Urumi gateway key, not the LLM provider key.

### Create a member key

An admin creates a member account or invitation through the dashboard's user/invitation workflow. A member can create another key for their own account through the dashboard key workflow, backed by POST /api/me/keys. The raw key is returned once; copy it into the MCP client secret configuration and do not commit it. If the dashboard workflow is unavailable, the API route requires an already authenticated gateway key.

### MCP Inspector

Open MCP Inspector, choose an HTTP/Streamable HTTP connection, set the URL to http://dashboard.urumi.local/mcp, and add the header:

~~~~text
Authorization: Bearer <user-api-key>
~~~~

Then initialize the connection, list tools, and run a harmless read operation.

### Claude Code

~~~~sh
claude mcp add --transport http urumi http://dashboard.urumi.local/mcp --header "Authorization: Bearer <user-api-key>"
~~~~

Use your production HTTPS host instead of the local URL for a remote deployment.

### Cursor

Add an MCP server entry to Cursor's MCP configuration (mcp.json):

~~~~json
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
~~~~

Replace the local URL for production and replace the placeholder with a real member key. Do not commit a populated configuration containing the key.

## How to use the chat agent

1. Open the dashboard at http://dashboard.urumi.local and sign in with a **Urumi Gateway API key**.
2. Open the dashboard's chat/agent area. The chat API is POST /api/chat.
3. Configure llm.baseUrl, llm.model, and secrets.llmApiKey in Helm values. The gateway reads them as LLM_BASE_URL, LLM_MODEL, and LLM_API_KEY and calls an OpenAI-compatible /chat/completions endpoint. The local values default to OpenRouter's https://openrouter.ai/api/v1 and model openrouter/free; llmApiKey is empty by default and must be supplied for live provider calls.
4. Try prompts such as:
   - Create a simple product named Demo Mug for 299.00 and publish it so it appears in the storefront.
   - What orders came in today? Summarize order IDs, statuses, totals, and payment methods.
5. The API response includes a tool_trace with each tool name and whether it returned an error. Tool calls execute through the gateway router under the logged-in user's identity and permissions; the router records audit events under that user.

Live chat success depends on a valid provider key, provider availability, and the selected model. A configured URL/model alone is not proof of a successful live provider call.

## Definition-of-done walkthrough

Use a disposable local cluster and test accounts. Do not revoke the only working admin key.

1. **Two users A and B:** sign in as admin, create two member accounts/invitations, and have each accept their own invitation and save the one-time key. Verify each key identifies the expected user through GET /api/me. **Needs live run.**
2. **Per-role tool permissions:** in the dashboard permissions workflow, deny a selected namespaced tool for role MEMBER. Verify it disappears from that member's tool list and a direct tools/call is rejected. The source checks permissions during listing and execution; live behavior needs verification.
3. **Revoke B's key:** use the admin key-management workflow to revoke B's key (backed by POST /api/keys/{kid}/revoke). Send another request using B's key and verify it returns unauthorized. The current revoke route is admin-only. **Needs live run.**
4. **Disable an upstream:** in the dashboard server registry, disable a disposable upstream. Verify its tools disappear and stale calls fail while another healthy upstream remains usable. **Needs live run.**
5. **Kill a pod:** from the repository's Kubernetes context, run kubectl delete pod -l app=weather-mcp in the disposable cluster, then watch kubectl get pods -w. Verify the Deployment replaces the pod and the service recovers. Do not delete PVCs. **Needs live run.**
6. **Audit log:** make a successful read call and a deliberately invalid/denied tool call, then inspect the admin audit view or GET /api/audit. Verify user, server, tool, source, duration and outcome. **Needs live run.**
7. **Store persistence:** place a COD order, note the order ID, restart WordPress/MySQL pods without deleting PVCs, and confirm the order remains in wp-admin. **Needs live run.**

The code contains the authorization, routing, audit and deployment paths described above. The steps marked **Needs live run** are not claimed as live acceptance results by this document.

## Bonus and stand-out items

These items have source evidence; this list does not claim production acceptance.

- **Per-role tool permissions at discovery and execution:** services/gateway/app/auth/rbac.py, services/gateway/app/routing/router.py, services/gateway/app/api/admin.py.
- **Upstream credential encryption in the gateway database:** services/gateway/app/auth/api_keys.py, services/gateway/app/api/admin.py, services/gateway/app/routing/router.py.
- **SSRF URL validation at registration, health refresh and execution:** services/gateway/app/api/admin.py, services/gateway/app/routing/router.py. Private and loopback addresses are not comprehensively blocked; see docs/threat-model.md.
- **Default-deny ingress and scoped workload NetworkPolicies, including database egress denial:** infrastructure/helm/urumi/templates/networkpolicy.yaml.
- **Non-root gateway and MCP containers:** infrastructure/helm/urumi/templates/gateway.yaml, infrastructure/helm/urumi/templates/mcp-servers.yaml.
- **Two-replica production gateway setting:** infrastructure/helm/urumi/values-prod.yaml. The tool cache is per replica; shared cache coordination is not implemented in the inspected source.

## Documentation

- [Architecture](docs/architecture.md)
- [System design](docs/system-design.md)
- [MCP request flow](docs/mcp-flow.md)
- [Threat model](docs/threat-model.md)
- [Implementation status](docs/STATUS.md)
- [Assignment evidence matrix](docs/assessment-gap-matrix.md)
- [Live acceptance tests](docs/live-acceptance-tests.md)
- [Store deployment runbook](docs/store-deployment-runbook.md)
- [Demo script](docs/demo-script.md)

## Verification commands

~~~~powershell
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
~~~~

These are verification commands, not results. See the demo script for the suggested recording order and the runbook for live-store and persistence gates.

## Known boundaries

- A successful local/unit test is not proof of browser checkout, pod restart persistence, or production-like k3s operation.
- Chat tool-calling requires a configured OpenAI-compatible provider; dashboard gateway authentication uses a **Urumi Gateway API key**, not the provider key.
- Invitation email delivery is not implemented; invitations are generated by the API/UI flow and shared as a one-time link/token.
- The local values use HTTP and local hostnames. Production values reference a TLS Secret but do not install cert-manager or issue certificates.
- The production values use placeholder DNS hosts and registry paths that must be replaced before deployment.
- The gateway tool cache is process-local; multiple replicas do not share cache invalidation.
- Kubernetes Secret encryption at rest, external secret management, backups/restore, and live monitoring are not configured by these chart files.

## Assignment handoff

The walkthrough covers the chart and trust boundaries, the running store/dashboard, the single gateway endpoint and namespaced tools, role/tool permissions, audit records, and persistence/failure-isolation procedures. Show only the behavior demonstrated by the current run or recording; distinguish source-level implementation from live acceptance evidence.

## Demo video

<!-- DEMO_VIDEO_LINK -->
