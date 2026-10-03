"""HTTP client for communicating with downstream Product Service."""

import logging
import time
from typing import Any, Dict
import httpx

from app.core.config import settings
from app.core.exceptions import ProductDependencyException, ProductTimeoutException
from app.core.logging import request_id_ctx

logger = logging.getLogger("order-service")


class ProductServiceClient:
    """Encapsulates outbound HTTP calls to Product Service with timeout and tracing."""

    def __init__(self, base_url: str = settings.PRODUCT_SERVICE_URL, timeout: float = settings.ORDER_TO_PRODUCT_TIMEOUT_SECONDS):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def check_availability(self, product_id: int, quantity: int) -> Dict[str, Any]:
        """Calls Product Service to verify inventory, price, and existence."""
        url = f"{self.base_url}/products/{product_id}/availability"
        params = {"quantity": quantity}
        request_id = request_id_ctx.get()
        headers = {"X-Request-ID": request_id} if request_id else {}

        start_time = time.perf_counter()
        logger.info(
            f"Calling Product Service: GET {url}?quantity={quantity}",
            extra={
                "dependency": "product-service",
                "dependency_url": url,
                "request_id": request_id,
            },
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=headers)
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

                if response.status_code == 404:
                    raise ProductDependencyException(
                        message=f"Product with ID {product_id} does not exist in catalog",
                        details={"product_id": product_id, "status_code": 404},
                        request_id=request_id,
                    )

                if response.status_code != 200:
                    logger.error(
                        f"Product Service returned error {response.status_code}",
                        extra={
                            "dependency": "product-service",
                            "dependency_url": url,
                            "status_code": response.status_code,
                            "duration_ms": duration_ms,
                            "request_id": request_id,
                        },
                    )
                    raise ProductDependencyException(
                        message=f"Product Service returned status {response.status_code}",
                        details={"status_code": response.status_code},
                        request_id=request_id,
                    )

                return response.json()

        except httpx.TimeoutException:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                f"Product Service timed out after {self.timeout}s (elapsed: {duration_ms}ms)",
                extra={
                    "dependency": "product-service",
                    "dependency_url": url,
                    "duration_ms": duration_ms,
                    "error_type": "TimeoutException",
                    "request_id": request_id,
                },
            )
            raise ProductTimeoutException(timeout_seconds=self.timeout, request_id=request_id)

        except httpx.RequestError as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                f"Failed to connect to Product Service at {url}: {exc}",
                extra={
                    "dependency": "product-service",
                    "dependency_url": url,
                    "duration_ms": duration_ms,
                    "error_type": type(exc).__name__,
                    "request_id": request_id,
                },
            )
            raise ProductDependencyException(
                message=f"Unable to reach Product Service at {self.base_url}",
                details={"error": str(exc)},
                request_id=request_id,
            )
