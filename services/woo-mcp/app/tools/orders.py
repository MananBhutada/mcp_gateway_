from ..woocommerce import request


ALLOWED_ORDER_STATUSES = {"pending", "processing", "on-hold", "completed", "cancelled", "refunded", "failed"}
ALLOWED_BILLING_FIELDS = {
    "first_name", "last_name", "company", "address_1", "address_2",
    "city", "state", "postcode", "country", "email", "phone",
}


def validate_order_id(order_id: int) -> int:
    try:
        value = int(order_id)
    except (TypeError, ValueError):
        raise ValueError("order_id must be a positive integer")
    if value <= 0:
        raise ValueError("order_id must be a positive integer")
    return value


def validate_line_items(line_items: list[dict]) -> list[dict]:
    """Allow only product IDs and positive quantities; WooCommerce resolves prices."""
    if not isinstance(line_items, list) or not line_items or len(line_items) > 50:
        raise ValueError("line_items must contain between 1 and 50 items")
    normalized = []
    for item in line_items:
        if not isinstance(item, dict):
            raise ValueError("each line item must be an object")
        try:
            product_id = int(item.get("product_id", 0))
            quantity = int(item.get("quantity", 0))
        except (TypeError, ValueError):
            raise ValueError("product_id and quantity must be positive integers")
        if product_id <= 0 or quantity <= 0 or quantity > 1000:
            raise ValueError("product_id and quantity must be positive integers; quantity must not exceed 1000")
        normalized.append({"product_id": product_id, "quantity": quantity})
    return normalized


def _o(o):
    billing = o.get("billing") or {}
    return {"id": o["id"], "status": o["status"], "total": o["total"], "currency": o["currency"],
            "date_created": o["date_created"], "payment_method": o.get("payment_method_title"),
            "customer": f'{billing.get("first_name", "")} {billing.get("last_name", "")}'.strip(),
            "items": [{"name": i.get("name", ""), "quantity": i.get("quantity", 0)}
                      for i in o.get("line_items", [])]}


def register(mcp):
    @mcp.tool()
    async def get_orders(after: str = "", status: str = "any", per_page: int = 20) -> list[dict]:
        """Get WooCommerce orders (assignment-compatible tool name); customer details are minimized."""
        params = {"per_page": max(1, min(per_page, 100)), "status": status}
        if after and after.strip():
            params["after"] = after.strip()[:40]
        return [_o(o) for o in await request("GET", "/orders", params)]

    @mcp.tool()
    async def list_orders(after: str = "", status: str = "any", per_page: int = 20) -> list[dict]:
        """List orders. The after parameter is an ISO8601 datetime; customer details are minimized."""
        params = {"per_page": max(1, min(per_page, 100)), "status": status}
        if after and after.strip():
            params["after"] = after.strip()[:40]
        return [_o(o) for o in await request("GET", "/orders", params)]

    @mcp.tool()
    async def create_order(line_items: list[dict], billing: dict | None = None,
                          payment_method: str = "cod") -> dict:
        """Create a WooCommerce order by product ID and quantity; defaults to cash on delivery."""
        items = validate_line_items(line_items)
        if payment_method != "cod":
            raise ValueError("payment_method must be 'cod' for the configured demo checkout")
        if billing is not None and not isinstance(billing, dict):
            raise ValueError("billing must be an object")
        clean_billing = {}
        for key, value in (billing or {}).items():
            if key not in ALLOWED_BILLING_FIELDS:
                raise ValueError(f"unsupported billing field: {key}")
            if not isinstance(value, str):
                raise ValueError(f"billing field {key} must be a string")
            if len(value) > 200:
                raise ValueError(f"billing field {key} is too long")
            clean_billing[key] = value.strip()
        body = {
            "status": "pending",
            "payment_method": "cod",
            "payment_method_title": "Cash on delivery",
            "set_paid": False,
            "line_items": items,
        }
        if clean_billing:
            body["billing"] = clean_billing
        return _o(await request("POST", "/orders", json=body))

    @mcp.tool()
    async def get_order(order_id: int) -> dict:
        """Get one order by positive numeric id."""
        return _o(await request("GET", f"/orders/{validate_order_id(order_id)}"))

    @mcp.tool()
    async def update_order_status(order_id: int, status: str) -> dict:
        """Update an order status to a supported WooCommerce status."""
        order_id = validate_order_id(order_id)
        if not isinstance(status, str) or status not in ALLOWED_ORDER_STATUSES:
            raise ValueError(f"status must be one of {sorted(ALLOWED_ORDER_STATUSES)}")
        return _o(await request("PUT", f"/orders/{order_id}", json={"status": status}))
