"""Tests for Product Service liveness and readiness probe endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_returns_healthy(client: AsyncClient):
    """Liveness probe must return 200 with service identifier."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "product-service"


@pytest.mark.asyncio
async def test_readiness_check_when_database_connected(client: AsyncClient):
    """Readiness probe must return 200 when database connectivity is verified."""
    response = await client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_readiness_check_when_simulated_unready(client: AsyncClient):
    """Simulated readiness toggle must cause /ready to return 503 while /health remains 200."""
    # Toggle unready
    toggle_resp = await client.post("/dev/faults/readiness-toggle?unready=true")
    assert toggle_resp.status_code == 200

    # Liveness must still be 200 (process is alive)
    liveness_resp = await client.get("/health")
    assert liveness_resp.status_code == 200

    # Readiness must now fail with 503 (traffic removed)
    readiness_resp = await client.get("/ready")
    assert readiness_resp.status_code == 503

    # Reset toggle
    await client.post("/dev/faults/readiness-toggle?unready=false")
    reset_resp = await client.get("/ready")
    assert reset_resp.status_code == 200
