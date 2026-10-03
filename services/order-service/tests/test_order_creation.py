"""Tests for order creation workflow and total calculations."""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_order_success(client: AsyncClient):
    """Test successful order creation with validated product and calculated total."""
    mock_availability = {
        "product_id": 1,
        "name": "Cloud Native Kubernetes Guide",
        "price": "39.99",
        "requested_quantity": 2,
        "available": True,
        "current_stock": 50,
    }

    with patch("app.clients.product_client.ProductServiceClient.check_availability", new_callable=AsyncMock) as mock_check:
        mock_check.return_value = mock_availability

        payload = {
            "items": [
                {"product_id": 1, "quantity": 2}
            ]
        }
        resp = await client.post("/orders", json=payload)
        assert resp.status_code == 201
        order = resp.json()

        assert order["id"] is not None
        assert order["status"] == "CONFIRMED"
        # 39.99 * 2 = 79.98
        assert float(order["total"]) == 79.98
        assert len(order["items"]) == 1
        assert order["items"][0]["product_id"] == 1
        assert order["items"][0]["product_name"] == "Cloud Native Kubernetes Guide"
        assert order["items"][0]["quantity"] == 2

        # Verify we can fetch it by ID
        get_resp = await client.get(f"/orders/{order['id']}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == order["id"]


@pytest.mark.asyncio
async def test_create_order_insufficient_stock(client: AsyncClient):
    """Order creation must return 409 if requested quantity exceeds stock."""
    mock_availability = {
        "product_id": 2,
        "name": "Observability Toolkit",
        "price": "49.50",
        "requested_quantity": 100,
        "available": False,
        "current_stock": 10,
    }

    with patch("app.clients.product_client.ProductServiceClient.check_availability", new_callable=AsyncMock) as mock_check:
        mock_check.return_value = mock_availability

        payload = {
            "items": [
                {"product_id": 2, "quantity": 100}
            ]
        }
        resp = await client.post("/orders", json=payload)
        assert resp.status_code == 409
        body = resp.json()
        assert body["error"]["code"] == "INSUFFICIENT_STOCK"
