"""Downstream HTTP proxy client for Order Service."""

import logging
import time
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.core.exceptions import DownstreamServiceException, GatewayTimeoutException, ServiceUnreachableException
from app.core.logging import request_id_ctx

logger = logging.getLogger("api-gateway")


class OrderClient:
    """Handles reverse proxy calls to Order Service."""

    def __init__(self, base_url: str = settings.ORDER_SERVICE_URL, timeout: float = settings.GATEWAY_REQUEST_TIMEOUT_SECONDS):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        req_id = request_id_ctx.get()
        return {"X-Request-ID": req_id} if req_id else {}

    async def list_orders(self, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}/orders"
        return await self._request("GET", url, params=params)

    async def get_order(self, order_id: int) -> Any:
        url = f"{self.base_url}/orders/{order_id}"
        return await self._request("GET", url)

    async def create_order(self, payload: Dict[str, Any]) -> Any:
        url = f"{self.base_url}/orders"
        return await self._request("POST", url, json=payload)

    async def ping_health(self) -> bool:
        """Pings order service /health for readiness check."""
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
                        dependency="order-service",
                        status_code=response.status_code,
                        message=detail,
                        details={"downstream_status": response.status_code},
                        request_id=req_id,
                    )

                return response.json()

        except httpx.TimeoutException:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.error(
                f"Order Service timed out after {self.timeout}s",
                extra={
                    "dependency": "order-service",
                    "dependency_url": url,
                    "duration_ms": duration_ms,
                    "request_id": req_id,
                },
            )
            raise GatewayTimeoutException(
                dependency="order-service",
                timeout_seconds=self.timeout,
                request_id=req_id,
            )

        except httpx.RequestError as exc:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.error(
                f"Unable to reach Order Service at {url}: {exc}",
                extra={
                    "dependency": "order-service",
                    "dependency_url": url,
                    "duration_ms": duration_ms,
                    "error_type": type(exc).__name__,
                    "request_id": req_id,
                },
            )
            raise ServiceUnreachableException(
                dependency="order-service",
                url=self.base_url,
                reason=str(exc),
                request_id=req_id,
            )
