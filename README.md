# Internet Shop — лабораторна робота №8, варіант 3

Асинхронний REST API інтернет-магазину на FastAPI. Дані зберігаються у SQLite через SQLAlchemy.

## Можливості
- CRUD для товарів: GET, POST, PATCH, DELETE.
- Фільтрація за категорією та пошук за назвою.
- Купівля товару зі зменшенням залишку в транзакції.
- Найдорожчий товар і загальна вартість залишків.
- Pydantic validation, HTTP status codes, Swagger UI.
- Асинхронний HTTPX-клієнт: `Task`, `gather`, `Semaphore`, timeout і retry.
- Автоматизовані API-тести.

## Запуск у Windows PowerShell
```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -e ".[test]"
uvicorn internet_shop.api:app --reload
```
Документація: http://127.0.0.1:8000/docs

## Тести
```powershell
python -m pytest -v
```

## Основні endpoints
- `GET /` — перевірка API.
- `GET /products?category_id=1&search=phone` — список і фільтри.
- `GET /products/{product_id}` — один товар.
- `POST /products` — створення товару.
- `PATCH /products/{product_id}` — часткове оновлення.
- `DELETE /products/{product_id}` — видалення.
- `GET /categories/{category_id}/products` — товари категорії.
- `POST /products/{product_id}/purchase` — купівля.
- `GET /products/statistics/summary` — найдорожчий товар і вартість залишків.
- `POST /products/batch` — асинхронне отримання кількох товарів через HTTPX.

База `shop.db` створюється автоматично. Для лабораторного демонстраційного проєкту використано SQLite, щоб запуск не вимагав окремого сервера БД.
