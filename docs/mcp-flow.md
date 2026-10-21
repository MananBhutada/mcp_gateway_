# MCP request flow

## Discovery

1. Client sends an MCP `initialize` request to the gateway's `/mcp` endpoint with `Authorization: Bearer <user-key>`.
2. Gateway authenticates the key and resolves the user/role.
3. `tools/list` gathers tools from enabled and reachable upstreams.
4. Names are prefixed with the upstream identifier, for example `woocommerce__list_products`, to avoid collisions.
5. The gateway filters discovery by the caller's role and tool permissions.

## Tool call

1. Client sends `tools/call` with a namespaced tool name and arguments.
2. Gateway validates the request, parses the upstream prefix and checks permission again at execution time.
3. Gateway opens an upstream session with timeout/error handling and invokes the selected tool.
4. Gateway records an audit event including caller, server, tool, duration and outcome.
5. Gateway returns a safe result or error; secrets and raw upstream internals are not returned.

## Health, disable and failure isolation

- Periodic/on-demand health checks update upstream status.
- Disabled or unreachable upstream tools should not be advertised as available.
- A stale tool call must still be checked at execution time and rejected if the tool is no longer allowed.
- Each upstream call has a bounded timeout so one failing server does not stall unrelated upstreams.

## Security boundary

The gateway is the client-facing authorization boundary. Clients must not bypass it to call upstream MCP servers directly. WooCommerce operations flow from Woo MCP to the WooCommerce REST API, not to MySQL directly. The actual behavior must be confirmed with live acceptance tests.
