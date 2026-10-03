"""API route tests for product catalog and inventory availability."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_product(client: AsyncClient):
    """Test creating a product and fetching it by ID."""
    payload = {
        "name": "Kubernetes in Practice",
        "description": "Production patterns for distributed systems",
        "price": 45.00,
        "stock": 10,
    }
    create_resp = await client.post("/products", json=payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["id"] is not None
    assert created["name"] == payload["name"]
    assert float(created["price"]) == 45.00
    assert created["stock"] == 10

    # Retrieve by ID
    get_resp = await client.get(f"/products/{created['id']}")
    assert get_resp.status_code == 200
    retrieved = get_resp.json()
    assert retrieved["id"] == created["id"]
    assert retrieved["name"] == payload["name"]


@pytest.mark.asyncio
async def test_get_nonexistent_product_returns_404(client: AsyncClient):
    """Attempting to retrieve a missing product ID must return structured 404 error."""
    resp = await client.get("/products/99999")
    assert resp.status_code == 404
    body = resp.json()
    assert "error" in body
    assert body["error"]["code"] == "PRODUCT_NOT_FOUND"


@pytest.mark.asyncio
async def test_check_availability(client: AsyncClient):
    """Test checking item availability for order service."""
    payload = {
        "name": "Microservices Book",
        "description": "Clean architecture guide",
        "price": 30.00,
        "stock": 5,
    }
    create_resp = await client.post("/products", json=payload)
    product_id = create_resp.json()["id"]

    # Check available quantity (3 <= 5)
    avail_resp = await client.get(f"/products/{product_id}/availability?quantity=3")
    assert avail_resp.status_code == 200
    avail_data = avail_resp.json()
    assert avail_data["available"] is True
    assert avail_data["current_stock"] == 5

    # Check excess quantity (10 > 5)
    unavail_resp = await client.get(f"/products/{product_id}/availability?quantity=10")
    assert unavail_resp.status_code == 200
    unavail_data = unavail_resp.json()
    assert unavail_data["available"] is False


@pytest.mark.asyncio
async def test_list_products_and_search(client: AsyncClient):
    """Test product list pagination and search filtering."""
    p1 = {"name": "Golang Handbook", "description": "Go concurrency", "price": 25.00, "stock": 20}
    p2 = {"name": "Python Fastapi", "description": "High performance async APIs", "price": 35.00, "stock": 15}
    await client.post("/products", json=p1)
    await client.post("/products", json=p2)

    # Search by keyword
    search_resp = await client.get("/products?search=Fastapi")
    assert search_resp.status_code == 200
    data = search_resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Python Fastapi"
