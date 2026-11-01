from sqlalchemy import select
from sqlalchemy.orm import Session
from internet_shop.models import Category, Product


class ProductRepository:
    """Database access for products and categories."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_products(self, category_id: int | None = None, search: str | None = None) -> list[Product]:
        statement = select(Product).order_by(Product.id)
        if category_id is not None:
            statement = statement.where(Product.category_id == category_id)
        if search:
            statement = statement.where(Product.name.ilike(f"%{search}%"))
        return list(self.session.scalars(statement))

    def get_product(self, product_id: int) -> Product | None:
        return self.session.get(Product, product_id)

    def add_product(self, product: Product) -> Product:
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def delete_product(self, product: Product) -> None:
        self.session.delete(product)
        self.session.commit()

    def category_exists(self, category_id: int) -> bool:
        return self.session.get(Category, category_id) is not None
