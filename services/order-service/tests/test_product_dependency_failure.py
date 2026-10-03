"""Tests demonstrating Order Service behavior when Product Service dependency fails."""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient

from app.core.exceptions import ProductDependencyException, ProductTimeoutException


@pytest.mark.asyncio
async def test_order_creation_handles_product_service_timeout(client: AsyncClient):
    """When Product Service exceeds timeout, Order Service returns 504 with structured error."""
    with patch(
        "app.clients.product_client.ProductServiceClient.check_availability",
        side_effect=ProductTimeoutException(timeout_seconds=2.5),
    ):
        payload = {"items": [{"product_id": 1, "quantity": 1}]}
        resp = await client.post("/orders", json=payload)
        assert resp.status_code == 504
        data = resp.json()
        assert "error" in data
        assert data["error"]["code"] == "PRODUCT_SERVICE_TIMEOUT"
        assert data["error"]["dependency"] == "product-service"


@pytest.mark.asyncio
async def test_order_creation_handles_product_service_unreachable(client: AsyncClient):
    """When Product Service connection fails, Order Service returns 502."""
    with patch(
        "app.clients.product_client.ProductServiceClient.check_availability",
        side_effect=ProductDependencyException(message="Unable to reach Product Service"),
    ):
        payload = {"items": [{"product_id": 1, "quantity": 1}]}
        resp = await client.post("/orders", json=payload)
        assert resp.status_code == 502
        data = resp.json()
        assert "error" in data
        assert data["error"]["code"] == "PRODUCT_SERVICE_UNAVAILABLE"
        assert data["error"]["dependency"] == "product-service"
