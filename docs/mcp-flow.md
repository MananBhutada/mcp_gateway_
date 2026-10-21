# MCP request flow

## Discovery
1. Client sends `initialize` to gateway `/mcp` with `Authorization: Bearer <user-key>`.
2. Gateway authenticates the key and resolves user/role.
3. `tools/list` gathers tools from enabled/reachable upstreams.
4. Names are prefixed with the upstream identifier, e.g. `woocommerce__list_products`.
5. The gateway applies role and tool permissions to discovery.

## Tool call
1. Client sends `tools/call` with a namespaced tool and arguments.
2. Gateway validates the request, resolves the upstream and checks permission again at execution time.
3. Gateway invokes the upstream using a bounded timeout and per-call session.
4. Gateway records an audit event with caller, server, tool, duration and outcome.
5. Gateway returns a safe result/error; upstream secrets and raw internal details are not returned.

## Health and failure isolation
- Health refresh updates upstream status.
- Disabled/unreachable upstream tools should not be advertised as available.
- Stale tool calls are checked again at execution time.
- One failing upstream must not block healthy upstreams.

## Security boundary
Clients and chat must call tools through the gateway, not directly against upstreams. WooCommerce MCP uses the WooCommerce REST API; the gateway does not query MySQL for commerce operations. Confirm live behavior with the acceptance tests.
