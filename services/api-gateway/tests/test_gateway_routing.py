"""Tests for API Gateway request routing and correlation ID propagation."""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "api-gateway"


@pytest.mark.asyncio
async def test_route_to_products(client: AsyncClient):
    """Verifies GET /api/products proxies to ProductClient."""
    mock_products = {
        "total": 1,
        "items": [{"id": 1, "name": "K8s Book", "price": 40.0, "stock": 10}],
    }

    with patch("app.api.routes.products.client.list_products", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_products
        resp = await client.get("/api/products")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
        assert "X-Request-ID" in resp.headers


@pytest.mark.asyncio
async def test_route_to_orders(client: AsyncClient):
    """Verifies POST /api/orders proxies to OrderClient."""
    mock_order = {"id": 101, "status": "CONFIRMED", "total": 80.0, "items": []}

    with patch("app.api.routes.orders.client.create_order", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_order
        resp = await client.post("/api/orders", json={"items": [{"product_id": 1, "quantity": 2}]})
        assert resp.status_code == 201
        assert resp.json()["id"] == 101
        assert "X-Request-ID" in resp.headers
