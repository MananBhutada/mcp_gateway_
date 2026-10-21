import os

from mcp.server.fastmcp import FastMCP
from .tools import products, orders, customers

mcp = FastMCP("woocommerce", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
products.register(mcp)
orders.register(mcp)
customers.register(mcp)
