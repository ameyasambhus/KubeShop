"""Standardized exception definitions for Order Service."""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable explanation")
    request_id: Optional[str] = Field(None, description="Correlation ID for tracing")
    dependency: Optional[str] = Field(None, description="Downstream dependency identifier if applicable")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ErrorResponse(BaseModel):
    error: ErrorDetail


class AppBaseException(HTTPException):
    """Base class for all structured application exceptions in Order Service."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        dependency: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message
        self.dependency = dependency
        self.details = details
        self.request_id = request_id


class OrderNotFoundException(AppBaseException):
    def __init__(self, order_id: int, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="ORDER_NOT_FOUND",
            message=f"Order with ID {order_id} does not exist",
            details={"order_id": order_id},
            request_id=request_id,
        )


class ProductDependencyException(AppBaseException):
    """Raised when Product Service fails or returns an unexpected error."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="PRODUCT_SERVICE_UNAVAILABLE",
            message=message,
            dependency="product-service",
            details=details,
            request_id=request_id,
        )


class ProductTimeoutException(AppBaseException):
    """Raised when calling Product Service exceeds the configured timeout."""
    def __init__(self, timeout_seconds: float, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            code="PRODUCT_SERVICE_TIMEOUT",
            message=f"Product Service failed to respond within {timeout_seconds} seconds",
            dependency="product-service",
            details={"timeout_seconds": timeout_seconds},
            request_id=request_id,
        )


class ItemOutOfStockException(AppBaseException):
    def __init__(self, product_id: int, requested: int, available: int, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="INSUFFICIENT_STOCK",
            message=f"Product {product_id} is out of stock or has insufficient quantity",
            details={"product_id": product_id, "requested": requested, "available": available},
            request_id=request_id,
        )
