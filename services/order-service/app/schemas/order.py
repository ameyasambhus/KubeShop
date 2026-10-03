"""Pydantic schemas for Order Service request validation and response formatting."""

from datetime import datetime
from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreate(BaseModel):
    product_id: int = Field(..., gt=0, description="Product ID to purchase")
    quantity: int = Field(..., gt=0, le=100, description="Quantity to purchase")


class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(..., min_length=1, description="List of items in the order")


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    unit_price: Decimal
    quantity: int


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    total: Decimal
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]


class OrderListResponse(BaseModel):
    total: int
    items: List[OrderResponse]
