"""Repository encapsulating database operations for Order and OrderItem entities."""

from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.order_item import OrderItem


class OrderRepository:
    """Handles raw SQL and ORM queries for the orders and order_items tables."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """Fetch order by primary key with related order items preloaded."""
        stmt = select(Order).where(Order.id == order_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_orders(self, skip: int = 0, limit: int = 50) -> Tuple[List[Order], int]:
        """Retrieve paginated orders ordered by creation date descending."""
        count_query = select(func.count(Order.id))
        count_res = await self.session.execute(count_query)
        total = count_res.scalar_one()

        stmt = select(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def create_order(self, status: str, total: Decimal, items_data: List[dict]) -> Order:
        """Create an order along with its child line items in a single transaction."""
        order = Order(status=status, total=total)
        self.session.add(order)
        await self.session.flush()

        for item in items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                product_name=item["product_name"],
                unit_price=item["unit_price"],
                quantity=item["quantity"],
            )
            self.session.add(order_item)

        await self.session.flush()
        await self.session.refresh(order)
        return order

    async def ping_database(self) -> bool:
        """Check PostgreSQL connectivity for the readiness probe."""
        try:
            await self.session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
