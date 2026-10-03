"""API Gateway routing for order management requests."""

from typing import Optional
from fastapi import APIRouter, Query, Request, status
from app.clients.order_client import OrderClient

router = APIRouter(prefix="/api/orders", tags=["Gateway Orders Proxy"])
client = OrderClient()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_order(request: Request):
    """Routes POST /api/orders to Order Service."""
    payload = await request.json()
    return await client.create_order(payload=payload)


@router.get("", status_code=status.HTTP_200_OK)
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Routes GET /api/orders to Order Service."""
    params = {"skip": skip, "limit": limit}
    return await client.list_orders(params=params)


@router.get("/{order_id}", status_code=status.HTTP_200_OK)
async def get_order(order_id: int):
    """Routes GET /api/orders/{id} to Order Service."""
    return await client.get_order(order_id=order_id)
