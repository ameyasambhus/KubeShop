"""Order API routes."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.product_client import ProductServiceClient
from app.db.session import get_db
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderListResponse, OrderResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


def get_order_service(session: AsyncSession = Depends(get_db)) -> OrderService:
    """Dependency provider for OrderService."""
    repository = OrderRepository(session)
    product_client = ProductServiceClient()
    return OrderService(repository, product_client)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    service: OrderService = Depends(get_order_service),
):
    """Create a new order after verifying product prices and stock availability."""
    return await service.create_order(order_in=order_in)


@router.get("", response_model=OrderListResponse, status_code=status.HTTP_200_OK)
async def list_orders(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: OrderService = Depends(get_order_service),
):
    """Retrieve list of existing orders."""
    items, total = await service.list_orders(skip=skip, limit=limit)
    return OrderListResponse(total=total, items=items)


@router.get("/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
async def get_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
):
    """Retrieve an existing order by its unique ID."""
    return await service.get_order(order_id=order_id)
