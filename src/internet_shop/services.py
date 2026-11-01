from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from internet_shop.models import Category, Product
from internet_shop.repositories import ProductRepository
from internet_shop.schemas import ProductCreate, ProductPatch


def create_category(session: Session, name: str) -> Category:
    """Create a category, rejecting duplicate names."""
    existing = session.scalar(select(Category).where(Category.name == name))
    if existing:
        raise HTTPException(status_code=409, detail="Category already exists")
    category = Category(name=name)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def create_product(session: Session, data: ProductCreate) -> Product:
    """Validate the referenced category and save a product."""
    repository = ProductRepository(session)
    if not repository.category_exists(data.category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    product = Product(**data.model_dump())
    return repository.add_product(product)


def update_product(session: Session, product_id: int, data: ProductPatch) -> Product:
    """Apply only supplied fields to a product."""
    repository = ProductRepository(session)
    product = repository.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    changes = data.model_dump(exclude_unset=True)
    if "category_id" in changes and changes["category_id"] is not None:
        if not repository.category_exists(changes["category_id"]):
            raise HTTPException(status_code=404, detail="Category not found")
    for field, value in changes.items():
        if value is not None:
            setattr(product, field, value)
    session.commit()
    session.refresh(product)
    return product


def purchase_product(session: Session, product_id: int, quantity: int) -> dict:
    """Decrease stock atomically in a database transaction."""
    try:
        product = session.scalar(
            select(Product).where(Product.id == product_id).with_for_update()
        )
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        if product.quantity < quantity:
            raise HTTPException(status_code=409, detail="Not enough stock")
        product.quantity -= quantity
        result = {
            "product_id": product.id,
            "purchased_quantity": quantity,
            "unit_price": product.price,
            "total_price": round(product.price * quantity, 2),
            "remaining_quantity": product.quantity,
        }
        session.commit()
        return result
    except Exception:
        session.rollback()
        raise


def shop_summary(session: Session) -> dict:
    """Calculate the most expensive item and total stock value."""
    products = list(session.scalars(select(Product)))
    most_expensive = max(products, key=lambda item: item.price, default=None)
    return {
        "most_expensive": most_expensive,
        "stock_value": round(sum(p.price * p.quantity for p in products), 2),
        "products_count": len(products),
    }
