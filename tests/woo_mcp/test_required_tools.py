import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "services/woo-mcp"))

from app.tools.orders import validate_line_items
from app.tools.customers import validate_customer_id, _customer


def test_create_order_accepts_only_product_ids_and_quantities():
    assert validate_line_items([
        {"product_id": 12, "quantity": 2, "price": "0.01", "arbitrary": "ignored"},
    ]) == [{"product_id": 12, "quantity": 2}]


@pytest.mark.parametrize("items", [[], [{}], [{"product_id": 0, "quantity": 1}],
                                    [{"product_id": 2, "quantity": 0}],
                                    [{"product_id": 2, "quantity": 1001}],
                                    [{"product_id": "not-an-id", "quantity": 1}],
                                    ["invalid"]])
def test_create_order_rejects_invalid_line_items(items):
    with pytest.raises(ValueError):
        validate_line_items(items)


@pytest.mark.parametrize("value,expected", [(1, 1), ("42", 42)])
def test_customer_id_accepts_positive_integer(value, expected):
    assert validate_customer_id(value) == expected


@pytest.mark.parametrize("value", [0, -1, None, "not-an-id"])
def test_customer_id_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        validate_customer_id(value)


def test_customer_projection_omits_address_phone_and_unrecognized_fields():
    result = _customer({
        "id": 42, "email": "customer@example.test", "first_name": "Ada", "last_name": "Lovelace",
        "username": "ada", "billing": {"city": "Pune", "country": "IN", "phone": "555-0100",
                                       "address_1": "private address"},
        "secret_field": "must not be returned",
    })
    assert result == {
        "id": 42, "email": "customer@example.test", "first_name": "Ada", "last_name": "Lovelace",
        "username": "ada", "billing_city": "Pune", "billing_country": "IN",
    }


def test_required_assignment_tool_names_are_registered():
    from app.tools import products, orders, customers

    class ToolRegistry:
        def __init__(self):
            self.registered = {}

        def tool(self):
            def decorator(function):
                self.registered[function.__name__] = function
                return function
            return decorator

    registry = ToolRegistry()
    products.register(registry)
    orders.register(registry)
    customers.register(registry)

    assert {"get_products", "get_orders", "create_order", "get_customer"} <= set(registry.registered)
