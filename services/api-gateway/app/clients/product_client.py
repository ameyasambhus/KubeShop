"""Downstream HTTP proxy client for Product Service."""

import logging
import time
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.core.exceptions import DownstreamServiceException, GatewayTimeoutException, ServiceUnreachableException
from app.core.logging import request_id_ctx

logger = logging.getLogger("api-gateway")


class ProductClient:
    """Handles reverse proxy calls to Product Service."""

    def __init__(self, base_url: str = settings.PRODUCT_SERVICE_URL, timeout: float = settings.GATEWAY_REQUEST_TIMEOUT_SECONDS):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        req_id = request_id_ctx.get()
        return {"X-Request-ID": req_id} if req_id else {}

    async def list_products(self, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}/products"
        return await self._request("GET", url, params=params)

    async def get_product(self, product_id: int) -> Any:
        url = f"{self.base_url}/products/{product_id}"
        return await self._request("GET", url)

    async def create_product(self, payload: Dict[str, Any]) -> Any:
        url = f"{self.base_url}/products"
        return await self._request("POST", url, json=payload)

    async def ping_health(self) -> bool:
        """Pings product service /health for readiness check."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/health")
                return res.status_code == 200
        except Exception:
            return False

    async def _request(self, method: str, url: str, **kwargs) -> Any:
        headers = self._headers()
        start = time.perf_counter()
        req_id = request_id_ctx.get()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, url, headers=headers, **kwargs)
                duration_ms = round((time.perf_counter() - start) * 1000, 2)

                if response.status_code >= 400:
                    try:
                        error_body = response.json()
                        detail = error_body.get("error", {}).get("message") or error_body.get("detail", response.text)
                    except Exception:
                        detail = response.text

                    raise DownstreamServiceException(
                        dependency="product-service",
                        status_code=response.status_code,
                        message=detail,
                        details={"downstream_status": response.status_code},
                        request_id=req_id,
                    )

                return response.json()

        except httpx.TimeoutException:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.error(
                f"Product Service timed out after {self.timeout}s",
                extra={
                    "dependency": "product-service",
                    "dependency_url": url,
                    "duration_ms": duration_ms,
                    "request_id": req_id,
                },
            )
            raise GatewayTimeoutException(
                dependency="product-service",
                timeout_seconds=self.timeout,
                request_id=req_id,
            )

        except httpx.RequestError as exc:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.error(
                f"Unable to reach Product Service at {url}: {exc}",
                extra={
                    "dependency": "product-service",
                    "dependency_url": url,
                    "duration_ms": duration_ms,
                    "error_type": type(exc).__name__,
                    "request_id": req_id,
                },
            )
            raise ServiceUnreachableException(
                dependency="product-service",
                url=self.base_url,
                reason=str(exc),
                request_id=req_id,
            )
