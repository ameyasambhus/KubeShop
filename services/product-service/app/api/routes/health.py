"""Kubernetes liveness and readiness probe endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService

router = APIRouter(tags=["Health & Probes"])

# In-memory toggle for simulating manual readiness failure during Kubernetes drills
SIMULATED_UNREADY = False


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Liveness probe: returns 200 if the process is alive.

    Does NOT check external dependencies so Kubernetes does not restart a pod
    simply because a database is briefly down.
    """
    return {
        "status": "healthy",
        "service": "product-service",
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(session: AsyncSession = Depends(get_db)):
    """Readiness probe: returns 200 only if the service can currently process requests.

    Verifies database connectivity. If the database is unreachable, returns 503 so
    Kubernetes stops sending traffic to this Pod via Service endpoints.
    """
    global SIMULATED_UNREADY
    if SIMULATED_UNREADY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unready", "reason": "simulated readiness failure"},
        )

    repository = ProductRepository(session)
    service = ProductService(repository)
    is_ready = await service.check_readiness()

    if not is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unready", "reason": "database unreachable"},
        )

    return {
        "status": "ready",
        "service": "product-service",
        "database": "connected",
    }
