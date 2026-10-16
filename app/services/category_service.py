from app import db
from app.models import Category


class CategoryService:
    @staticmethod
    def create_category(name: str) -> Category:
        name = name.strip()

        if not name:
            raise ValueError("Category name cannot be empty")

        existing = db.session.scalar(
            db.select(Category).where(Category.name == name)
        )

        if existing is not None:
            raise ValueError("Category already exists")

        category = Category(name=name)

        db.session.add(category)
        db.session.commit()

        return category

    @staticmethod
    def get_categories() -> list[Category]:
        return db.session.scalars(
            db.select(Category).order_by(Category.id)
        ).all()

    @staticmethod
    def get_category(category_id: int) -> Category | None:
        return db.session.get(Category, category_id)