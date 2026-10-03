"""Standardized exception definitions and HTTP response builders for Product Service."""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error explanation")
    request_id: Optional[str] = Field(None, description="Correlation ID for tracing")
    details: Optional[Dict[str, Any]] = Field(None, description="Optional diagnostic details")


class ErrorResponse(BaseModel):
    error: ErrorDetail


class AppBaseException(HTTPException):
    """Base class for all structured application exceptions."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message
        self.details = details
        self.request_id = request_id


class ProductNotFoundException(AppBaseException):
    def __init__(self, product_id: int, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="PRODUCT_NOT_FOUND",
            message=f"Product with ID {product_id} was not found",
            details={"product_id": product_id},
            request_id=request_id,
        )


class InsufficientStockException(AppBaseException):
    def __init__(self, product_id: int, requested: int, available: int, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="INSUFFICIENT_STOCK",
            message=f"Insufficient inventory for product {product_id}. Requested: {requested}, Available: {available}",
            details={"product_id": product_id, "requested": requested, "available": available},
            request_id=request_id,
        )


class DatabaseUnavailableException(AppBaseException):
    def __init__(self, message: str = "Database service is unreachable", request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="DATABASE_UNAVAILABLE",
            message=message,
            request_id=request_id,
        )
