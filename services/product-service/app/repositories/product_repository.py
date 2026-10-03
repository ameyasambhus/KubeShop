"""Repository encapsulating database operations for Product entities."""

from typing import List, Optional, Tuple
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    """Handles raw SQL and ORM queries for the products table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """Fetch a single product by its primary key ID."""
        stmt = select(Product).where(Product.id == product_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_products(
        self,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
    ) -> Tuple[List[Product], int]:
        """List products with optional substring search and pagination."""
        base_query = select(Product)
        count_query = select(func.count(Product.id))

        if search:
            search_filter = Product.name.ilike(f"%{search}%") | Product.description.ilike(f"%{search}%")
            base_query = base_query.where(search_filter)
            count_query = count_query.where(search_filter)

        # Get total count
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        # Get paged results ordered by ID
        paged_query = base_query.order_by(Product.id.asc()).offset(skip).limit(limit)
        result = await self.session.execute(paged_query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, product_in: ProductCreate) -> Product:
        """Insert a new product record."""
        product = Product(
            name=product_in.name,
            description=product_in.description,
            price=product_in.price,
            stock=product_in.stock,
        )
        self.session.add(product)
        await self.session.flush()
        await self.session.refresh(product)
        return product

    async def update(self, product: Product, product_in: ProductUpdate) -> Product:
        """Update existing product fields."""
        update_data = product_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        await self.session.flush()
        await self.session.refresh(product)
        return product

    async def decrement_stock(self, product_id: int, quantity: int) -> Optional[Product]:
        """Atomically decrement stock if sufficient inventory exists."""
        product = await self.get_by_id(product_id)
        if not product or product.stock < quantity:
            return None
        product.stock -= quantity
        await self.session.flush()
        await self.session.refresh(product)
        return product

    async def ping_database(self) -> bool:
        """Executes a lightweight query to test PostgreSQL connectivity for readiness probe."""
        try:
            await self.session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
