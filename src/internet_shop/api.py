import asyncio
import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from internet_shop.database import Base, engine, get_session
from internet_shop.models import Category, Product
from internet_shop.repositories import ProductRepository
from internet_shop.schemas import (
    BatchRequest, CategoryCreate, CategoryResponse, ProductCreate, ProductPatch,
    ProductResponse, PurchaseRequest, PurchaseResponse, ShopSummary,
)
from internet_shop.services import create_category, create_product, purchase_product, shop_summary, update_product
from internet_shop.external_api import fetch_many_products

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Internet Shop API", version="0.8.0",
              description="REST API для інтернет-магазину, лабораторна №8, варіант 3")


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"message": "Internet Shop API is running"}


@app.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def add_category(data: CategoryCreate, session: Session = Depends(get_session)) -> Category:
    return create_category(session, data.name.strip())


@app.get("/categories", response_model=list[CategoryResponse])
async def list_categories(session: Session = Depends(get_session)) -> list[Category]:
    return list(session.scalars(select(Category).order_by(Category.id)))


@app.get("/products", response_model=list[ProductResponse])
async def list_products(
    category_id: int | None = Query(default=None, gt=0),
    search: str | None = Query(default=None, min_length=1, max_length=120),
    session: Session = Depends(get_session),
) -> list[Product]:
    return ProductRepository(session).list_products(category_id, search)


@app.get("/products/statistics/summary", response_model=ShopSummary)
async def get_summary(session: Session = Depends(get_session)) -> dict:
    return shop_summary(session)


@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, session: Session = Depends(get_session)) -> Product:
    product = ProductRepository(session).get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def add_product(data: ProductCreate, session: Session = Depends(get_session)) -> Product:
    return create_product(session, data)


@app.patch("/products/{product_id}", response_model=ProductResponse)
async def patch_product(product_id: int, data: ProductPatch,
                        session: Session = Depends(get_session)) -> Product:
    return update_product(session, product_id, data)


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_product(product_id: int, session: Session = Depends(get_session)) -> None:
    repository = ProductRepository(session)
    product = repository.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    repository.delete_product(product)


@app.get("/categories/{category_id}/products", response_model=list[ProductResponse])
async def products_by_category(category_id: int, session: Session = Depends(get_session)) -> list[Product]:
    if session.get(Category, category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return ProductRepository(session).list_products(category_id=category_id)


@app.post("/products/{product_id}/purchase", response_model=PurchaseResponse)
async def purchase(product_id: int, data: PurchaseRequest,
                   session: Session = Depends(get_session)) -> dict:
    return purchase_product(session, product_id, data.quantity)


@app.post("/products/batch")
async def batch_products(data: BatchRequest) -> list[dict]:
    """Demonstrate async HTTP client, Task/gather, timeout, retry and Semaphore."""
    try:
        return await asyncio.wait_for(
            fetch_many_products("http://127.0.0.1:8000", data.product_ids),
            timeout=12.0,
        )
    except asyncio.TimeoutError as exc:
        raise HTTPException(status_code=504, detail="Batch request timed out") from exc
    except (httpx.RequestError, httpx.HTTPStatusError) as exc:
        raise HTTPException(status_code=502, detail="Unable to fetch one or more products") from exc
