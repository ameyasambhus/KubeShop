"""Tests verifying gateway error handling, timeout translation, and dependency failures."""

from unittest.mock import patch
import pytest
from httpx import AsyncClient

from app.core.exceptions import GatewayTimeoutException, ServiceUnreachableException


@pytest.mark.asyncio
async def test_gateway_timeout_translation(client: AsyncClient):
    """When downstream service times out, gateway returns standardized 504."""
    with patch(
        "app.api.routes.products.client.list_products",
        side_effect=GatewayTimeoutException(dependency="product-service", timeout_seconds=5.0),
    ):
        resp = await client.get("/api/products")
        assert resp.status_code == 504
        data = resp.json()
        assert "error" in data
        assert data["error"]["code"] == "GATEWAY_TIMEOUT"
        assert data["error"]["dependency"] == "product-service"


@pytest.mark.asyncio
async def test_gateway_service_unreachable_translation(client: AsyncClient):
    """When downstream service connection is refused, gateway returns standardized 502."""
    with patch(
        "app.api.routes.orders.client.list_orders",
        side_effect=ServiceUnreachableException(
            dependency="order-service",
            url="http://order-service:8000",
            reason="Connection refused",
        ),
    ):
        resp = await client.get("/api/orders")
        assert resp.status_code == 502
        data = resp.json()
        assert "error" in data
        assert data["error"]["code"] == "SERVICE_UNREACHABLE"
        assert data["error"]["dependency"] == "order-service"
