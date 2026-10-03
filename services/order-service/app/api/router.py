"""Centralized API router for Order Service."""

from fastapi import APIRouter

from app.api.routes import health, orders

api_router = APIRouter()

# Register core probe routes at root level for Kubernetes
api_router.include_router(health.router)

# Register order management routes
api_router.include_router(orders.router)
