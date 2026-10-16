from decimal import Decimal

from app import db
from app.models import Category, Product


class ProductService:
    @staticmethod
    def create_product(
        name: str,
        description: str,
        price: Decimal,
        stock_quantity: int,
        category_id: int,
    ) -> Product:
        if not name.strip():
            raise ValueError("Product name cannot be empty")

        if price < Decimal("0.00"):
            raise ValueError("Product price cannot be negative")

        if stock_quantity < 0:
            raise ValueError("Stock quantity cannot be negative")

        category = db.session.get(Category, category_id)

        if category is None:
            raise ValueError("Category not found")

        product = Product(
            name=name.strip(),
            description=description.strip(),
            price=price,
            stock_quantity=stock_quantity,
            category=category,
        )

        db.session.add(product)
        db.session.commit()

        # added on purpose
        # db.session.commit()
        
        return product

    @staticmethod
    def get_product(product_id: int) -> Product | None:
        return db.session.get(Product, product_id)

    @staticmethod
    def get_products(
        search: str = "",
    ) -> list[Product]:

        query = db.select(Product)

        if search:

            query = query.where(
                Product.name.ilike(
                    f"%{search}%"
                )
            )

        query = query.order_by(
            Product.name
        )

        return db.session.scalars(
            query
        ).all()