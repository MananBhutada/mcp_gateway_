from ..woocommerce import request


def validate_customer_id(customer_id: int) -> int:
    try:
        value = int(customer_id)
    except (TypeError, ValueError):
        raise ValueError("customer_id must be a positive integer")
    if value <= 0:
        raise ValueError("customer_id must be a positive integer")
    return value


def _customer(customer: dict) -> dict:
    # Deliberately avoid returning addresses, phone numbers, or arbitrary upstream fields.
    billing = customer.get("billing") or {}
    return {
        "id": customer["id"],
        "email": customer.get("email", ""),
        "first_name": customer.get("first_name", ""),
        "last_name": customer.get("last_name", ""),
        "username": customer.get("username", ""),
        "billing_city": billing.get("city", ""),
        "billing_country": billing.get("country", ""),
    }


def register(mcp):
    @mcp.tool()
    async def get_customer(customer_id: int) -> dict:
        """Look up a WooCommerce customer by numeric ID; returns a minimized customer profile."""
        return _customer(await request("GET", f"/customers/{validate_customer_id(customer_id)}"))
