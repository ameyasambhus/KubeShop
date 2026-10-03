"""Standardized exception definitions for API Gateway."""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable explanation")
    request_id: Optional[str] = Field(None, description="Correlation ID")
    dependency: Optional[str] = Field(None, description="Downstream service identifier")
    details: Optional[Dict[str, Any]] = Field(None, description="Detailed diagnostic info")


class ErrorResponse(BaseModel):
    error: ErrorDetail


class AppBaseException(HTTPException):
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


class GatewayTimeoutException(AppBaseException):
    def __init__(self, dependency: str, timeout_seconds: float, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            code="GATEWAY_TIMEOUT",
            message=f"Downstream service '{dependency}' did not respond within {timeout_seconds} seconds",
            dependency=dependency,
            details={"timeout_seconds": timeout_seconds},
            request_id=request_id,
        )


class DownstreamServiceException(AppBaseException):
    def __init__(self, dependency: str, status_code: int, message: str, details: Optional[Dict[str, Any]] = None, request_id: Optional[str] = None):
        super().__init__(
            status_code=status_code,
            code=f"{dependency.upper().replace('-', '_')}_ERROR",
            message=message,
            dependency=dependency,
            details=details,
            request_id=request_id,
        )


class ServiceUnreachableException(AppBaseException):
    def __init__(self, dependency: str, url: str, reason: str, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="SERVICE_UNREACHABLE",
            message=f"Unable to connect to downstream service '{dependency}' at {url}",
            dependency=dependency,
            details={"url": url, "reason": reason},
            request_id=request_id,
        )
