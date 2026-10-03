"""Product catalog and inventory API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.product_repository import ProductRepository
from app.schemas.product import (
    ProductAvailabilityResponse,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


def get_product_service(session: AsyncSession = Depends(get_db)) -> ProductService:
    """Dependency provider for ProductService."""
    repository = ProductRepository(session)
    return ProductService(repository)


@router.get("", response_model=ProductListResponse, status_code=status.HTTP_200_OK)
async def list_products(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Page limit"),
    search: Optional[str] = Query(None, description="Optional search term for product name/description"),
    service: ProductService = Depends(get_product_service),
):
    """Retrieve catalog products with optional search query."""
    items, total = await service.list_products(skip=skip, limit=limit, search=search)
    return ProductListResponse(total=total, items=items)


@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    """Retrieve a single product by its unique ID."""
    return await service.get_product(product_id=product_id)


@router.get(
    "/{product_id}/availability",
    response_model=ProductAvailabilityResponse,
    status_code=status.HTTP_200_OK,
)
async def check_availability(
    product_id: int,
    quantity: int = Query(1, ge=1, description="Quantity to verify against stock"),
    service: ProductService = Depends(get_product_service),
):
    """Verify item pricing and stock availability. Called by Order Service during checkout."""
    return await service.check_availability(product_id=product_id, quantity=quantity)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    service: ProductService = Depends(get_product_service),
):
    """Add a new product to the catalog."""
    return await service.create_product(product_in=product_in)


@router.patch("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    service: ProductService = Depends(get_product_service),
):
    """Update details or inventory for an existing product."""
    return await service.update_product(product_id=product_id, product_in=product_in)
