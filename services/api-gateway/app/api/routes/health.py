"""Health and readiness probe routes for API Gateway."""

from fastapi import APIRouter, status
from app.clients.order_client import OrderClient
from app.clients.product_client import ProductClient

router = APIRouter(tags=["Health & Probes"])

product_client = ProductClient()
order_client = OrderClient()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Liveness probe: verifies Gateway process is running."""
    return {
        "status": "healthy",
        "service": "api-gateway",
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """Readiness probe: reports gateway readiness and dependency connectivity status."""
    product_ok = await product_client.ping_health()
    order_ok = await order_client.ping_health()

    return {
        "status": "ready",
        "service": "api-gateway",
        "dependencies": {
            "product_service": "reachable" if product_ok else "unreachable",
            "order_service": "reachable" if order_ok else "unreachable",
        },
    }
