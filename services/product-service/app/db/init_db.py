"""Database initialization and automatic seed data population."""

import logging
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.base import Base
from app.db.session import async_session_factory
from app.models.product import Product

logger = logging.getLogger("product-service")

INITIAL_PRODUCTS = [
    {
        "name": "Cloud Native Kubernetes Guide",
        "description": "Comprehensive practical manual for deploying, scaling, and managing microservices on Kubernetes.",
        "price": Decimal("39.99"),
        "stock": 50,
    },
    {
        "name": "Microservices Observability Toolkit",
        "description": "A deep dive into distributed tracing, structured logging, Prometheus metrics, and automated root-cause analysis.",
        "price": Decimal("49.50"),
        "stock": 35,
    },
    {
        "name": "Production Incident Runbook",
        "description": "Real-world incident management, debugging CrashLoopBackOff, readiness failures, and OOMKilled containers.",
        "price": Decimal("29.00"),
        "stock": 100,
    },
    {
        "name": "Site Reliability Engineering Mug",
        "description": "Keep coffee hot during 3 AM pages and cascading outage remediation.",
        "price": Decimal("14.99"),
        "stock": 200,
    },
    {
        "name": "DevOps Mechanical Keyboard",
        "description": "Tactile clicky switches designed for rapid kubectl debugging and vim workflows.",
        "price": Decimal("119.00"),
        "stock": 15,
    },
]


async def init_db(engine: AsyncEngine) -> None:
    """Initializes tables and populates default catalog items if missing."""
    async with engine.begin() as conn:
        # Create tables if not present
        await conn.run_sync(Base.metadata.create_all)

    # Seed products if empty
    async with async_session_factory() as session:
        result = await session.execute(select(Product))
        existing = result.scalars().first()
        if existing is None:
            logger.info("Database empty. Seeding initial development products...")
            for item in INITIAL_PRODUCTS:
                product = Product(
                    name=item["name"],
                    description=item["description"],
                    price=item["price"],
                    stock=item["stock"],
                )
                session.add(product)
            await session.commit()
            logger.info("Successfully seeded %d products.", len(INITIAL_PRODUCTS))
        else:
            logger.info("Database already contains product data; skipping seed.")
