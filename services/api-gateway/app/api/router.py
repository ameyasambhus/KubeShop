"""Centralized API router for API Gateway."""

from fastapi import APIRouter

from app.api.routes import health, orders, products

api_router = APIRouter()

# Register core probe routes
api_router.include_router(health.router)

# Register proxied microservice routes
api_router.include_router(products.router)
api_router.include_router(orders.router)
