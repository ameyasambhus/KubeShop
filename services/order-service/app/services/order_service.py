"""Business logic orchestrating order creation, validation, and retrieval."""

import logging
from decimal import Decimal
from typing import List, Optional, Tuple

from app.clients.product_client import ProductServiceClient
from app.core.exceptions import ItemOutOfStockException, OrderNotFoundException
from app.models.order import Order
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate

logger = logging.getLogger("order-service")


class OrderService:
    """Manages order creation workflow and external catalog coordination."""

    def __init__(self, repository: OrderRepository, product_client: ProductServiceClient):
        self.repository = repository
        self.product_client = product_client

    async def create_order(self, order_in: OrderCreate) -> Order:
        """Validates products with Product Service, computes order total, and stores order."""
        total_amount = Decimal("0.00")
        validated_items = []

        logger.info("Processing order creation for %d items", len(order_in.items))

        # Validate each product against Product Service
        for item in order_in.items:
            availability_data = await self.product_client.check_availability(
                product_id=item.product_id,
                quantity=item.quantity,
            )

            if not availability_data.get("available", False):
                raise ItemOutOfStockException(
                    product_id=item.product_id,
                    requested=item.quantity,
                    available=availability_data.get("current_stock", 0),
                )

            unit_price = Decimal(str(availability_data["price"]))
            item_total = unit_price * item.quantity
            total_amount += item_total

            validated_items.append({
                "product_id": item.product_id,
                "product_name": availability_data["name"],
                "unit_price": unit_price,
                "quantity": item.quantity,
            })

        logger.info(
            "Calculated order total: %s USD across %d line items",
            total_amount,
            len(validated_items),
        )

        # Persist order and line items
        order = await self.repository.create_order(
            status="CONFIRMED",
            total=total_amount,
            items_data=validated_items,
        )
        return order

    async def get_order(self, order_id: int) -> Order:
        """Retrieve an existing order or raise 404."""
        order = await self.repository.get_by_id(order_id)
        if not order:
            raise OrderNotFoundException(order_id=order_id)
        return order

    async def list_orders(self, skip: int = 0, limit: int = 50) -> Tuple[List[Order], int]:
        """List orders with pagination."""
        return await self.repository.list_orders(skip=skip, limit=limit)

    async def check_readiness(self) -> bool:
        """Verify PostgreSQL connectivity for readiness probe."""
        return await self.repository.ping_database()
