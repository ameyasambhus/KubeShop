"""Unit tests for ProductRepository database queries."""

import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


@pytest.mark.asyncio
async def test_repository_crud_lifecycle(db_session: AsyncSession):
    repo = ProductRepository(db_session)

    # Create
    item_in = ProductCreate(
        name="Test Keyboard",
        description="Cherry MX Brown",
        price=Decimal("99.99"),
        stock=10,
    )
    product = await repo.create(item_in)
    assert product.id is not None
    assert product.name == "Test Keyboard"

    # Read
    fetched = await repo.get_by_id(product.id)
    assert fetched is not None
    assert fetched.name == "Test Keyboard"

    # Update
    update_in = ProductUpdate(price=Decimal("89.99"), stock=15)
    updated = await repo.update(fetched, update_in)
    assert updated.price == Decimal("89.99")
    assert updated.stock == 15

    # Decrement stock
    decremented = await repo.decrement_stock(product.id, 5)
    assert decremented is not None
    assert decremented.stock == 10

    # Decrement more than available returns None
    failed_dec = await repo.decrement_stock(product.id, 100)
    assert failed_dec is None
