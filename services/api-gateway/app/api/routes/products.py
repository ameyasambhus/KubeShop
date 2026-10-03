"""API Gateway routing for product catalog requests."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Query, Request, status
from app.clients.product_client import ProductClient

router = APIRouter(prefix="/api/products", tags=["Gateway Products Proxy"])
client = ProductClient()


@router.get("", status_code=status.HTTP_200_OK)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
):
    """Routes GET /api/products to Product Service."""
    params = {"skip": skip, "limit": limit}
    if search:
        params["search"] = search
    return await client.list_products(params=params)


@router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def get_product(product_id: int):
    """Routes GET /api/products/{id} to Product Service."""
    return await client.get_product(product_id=product_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_product(request: Request):
    """Routes POST /api/products to Product Service."""
    payload = await request.json()
    return await client.create_product(payload=payload)
