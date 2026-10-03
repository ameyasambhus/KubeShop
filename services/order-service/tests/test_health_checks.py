"""Tests for Order Service liveness and readiness probe endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_returns_healthy(client: AsyncClient):
    """Liveness probe must return 200 with service identifier."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "order-service"


@pytest.mark.asyncio
async def test_readiness_check_when_database_connected(client: AsyncClient):
    """Readiness probe must return 200 when database connectivity is verified."""
    response = await client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
