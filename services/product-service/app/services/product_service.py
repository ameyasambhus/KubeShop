"""Business logic layer for Product Service operations."""

import asyncio
import logging
from typing import List, Optional, Tuple

from app.core.config import settings
from app.core.exceptions import ProductNotFoundException
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductAvailabilityResponse, ProductCreate, ProductUpdate

logger = logging.getLogger("product-service")


class ProductService:
    """Encapsulates catalog and inventory management business logic."""

    def __init__(self, repository: ProductRepository):
        self.repository = repository

    async def _apply_simulated_delay(self) -> None:
        """Applies artificial latency if configured (used for Kubernetes timeout drills)."""
        if settings.SIMULATED_LATENCY_MS > 0:
            logger.warning(
                "Applying simulated latency of %d ms for testing",
                settings.SIMULATED_LATENCY_MS,
                extra={"simulated_latency_ms": settings.SIMULATED_LATENCY_MS},
            )
            await asyncio.sleep(settings.SIMULATED_LATENCY_MS / 1000.0)

    async def list_products(
        self,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
    ) -> Tuple[List[Product], int]:
        """Retrieve paginated catalog items."""
        await self._apply_simulated_delay()
        return await self.repository.list_products(skip=skip, limit=limit, search=search)

    async def get_product(self, product_id: int) -> Product:
        """Retrieve a specific product or raise 404."""
        await self._apply_simulated_delay()
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id=product_id)
        return product

    async def check_availability(self, product_id: int, quantity: int) -> ProductAvailabilityResponse:
        """Validates if requested quantity is available in stock. Used by Order Service."""
        await self._apply_simulated_delay()
        product = await self.get_product(product_id)
        is_available = product.stock >= quantity
        return ProductAvailabilityResponse(
            product_id=product.id,
            name=product.name,
            price=product.price,
            requested_quantity=quantity,
            available=is_available,
            current_stock=product.stock,
        )

    async def create_product(self, product_in: ProductCreate) -> Product:
        """Create a new catalog product."""
        return await self.repository.create(product_in)

    async def update_product(self, product_id: int, product_in: ProductUpdate) -> Product:
        """Update an existing catalog product."""
        product = await self.get_product(product_id)
        return await self.repository.update(product, product_in)

    async def check_readiness(self) -> bool:
        """Validates that underlying persistence is reachable."""
        return await self.repository.ping_database()
