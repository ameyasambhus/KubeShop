"""Kubernetes liveness and readiness probe endpoints for Order Service."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.product_client import ProductServiceClient
from app.db.session import get_db
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService

router = APIRouter(tags=["Health & Probes"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Liveness probe: returns 200 if process is alive.

    Does not verify external dependencies to prevent cascading restart loops.
    """
    return {
        "status": "healthy",
        "service": "order-service",
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(session: AsyncSession = Depends(get_db)):
    """Readiness probe: returns 200 if database connectivity is healthy.

    Returns 503 if Order DB is down so Kubernetes unroutes traffic from this Pod.
    """
    repository = OrderRepository(session)
    product_client = ProductServiceClient()
    service = OrderService(repository, product_client)

    is_ready = await service.check_readiness()
    if not is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unready", "reason": "database unreachable"},
        )

    return {
        "status": "ready",
        "service": "order-service",
        "database": "connected",
    }
