"""Centralized API router for Product Service."""

from fastapi import APIRouter

from app.api.routes import dev_faults, health, products
from app.core.config import settings

api_router = APIRouter()

# Register core probe routes at root level for standard Kubernetes health/readiness paths
api_router.include_router(health.router)

# Register product catalog routes
api_router.include_router(products.router)

# Register dev fault endpoints only in development mode
if settings.APP_ENV == "development":
    api_router.include_router(dev_faults.router)
