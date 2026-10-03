"""Pydantic schemas for Product Service request/response validation."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Product title")
    description: Optional[str] = Field(None, description="Detailed product description")
    price: Decimal = Field(..., gt=0, decimal_places=2, description="Unit price in USD")
    stock: int = Field(default=0, ge=0, description="Available stock quantity")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    stock: Optional[int] = Field(None, ge=0)


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique product identifier")
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    total: int = Field(..., description="Total count matching query")
    items: List[ProductResponse] = Field(..., description="List of products")


class ProductAvailabilityResponse(BaseModel):
    product_id: int
    name: str
    price: Decimal
    requested_quantity: int
    available: bool
    current_stock: int
