"""Database schema initialization for Order Service."""

import logging
from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.base import Base

logger = logging.getLogger("order-service")


async def init_db(engine: AsyncEngine) -> None:
    """Creates orders and order_items tables if they do not exist."""
    async with engine.begin() as conn:
        logger.info("Initializing Order Service database tables...")
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Order Service database initialization complete.")
