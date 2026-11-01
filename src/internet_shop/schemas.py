from pydantic import BaseModel, Field, ConfigDict


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=500)
    price: float = Field(gt=0, le=10_000_000)
    quantity: int = Field(ge=0, le=1_000_000)
    category_id: int = Field(gt=0)


class ProductPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    price: float | None = Field(default=None, gt=0, le=10_000_000)
    quantity: int | None = Field(default=None, ge=0, le=1_000_000)
    category_id: int | None = Field(default=None, gt=0)


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    price: float
    quantity: int
    category_id: int


class PurchaseRequest(BaseModel):
    quantity: int = Field(default=1, ge=1, le=1000)


class PurchaseResponse(BaseModel):
    product_id: int
    purchased_quantity: int
    unit_price: float
    total_price: float
    remaining_quantity: int


class ShopSummary(BaseModel):
    most_expensive: ProductResponse | None
    stock_value: float
    products_count: int


class BatchRequest(BaseModel):
    product_ids: list[int] = Field(min_length=1, max_length=20)
