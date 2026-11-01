def make_category(client):
    response = client.post("/categories", json={"name": "Electronics"})
    assert response.status_code == 201
    return response.json()["id"]


def make_product(client, category_id, **overrides):
    data = {
        "name": "Smartphone",
        "description": "Test product",
        "price": 500.0,
        "quantity": 5,
        "category_id": category_id,
    }
    data.update(overrides)
    return client.post("/products", json=data)


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Internet Shop API is running"


def test_create_and_get_product(client):
    category_id = make_category(client)
    created = make_product(client, category_id)
    assert created.status_code == 201
    product_id = created.json()["id"]
    fetched = client.get(f"/products/{product_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Smartphone"


def test_validation_rejects_negative_price(client):
    category_id = make_category(client)
    response = make_product(client, category_id, price=-1)
    assert response.status_code == 422


def test_patch_product(client):
    category_id = make_category(client)
    product_id = make_product(client, category_id).json()["id"]
    response = client.patch(f"/products/{product_id}", json={"price": 450})
    assert response.status_code == 200
    assert response.json()["price"] == 450


def test_delete_product(client):
    category_id = make_category(client)
    product_id = make_product(client, category_id).json()["id"]
    assert client.delete(f"/products/{product_id}").status_code == 204
    assert client.get(f"/products/{product_id}").status_code == 404


def test_purchase_reduces_stock(client):
    category_id = make_category(client)
    product_id = make_product(client, category_id).json()["id"]
    response = client.post(f"/products/{product_id}/purchase", json={"quantity": 2})
    assert response.status_code == 200
    assert response.json()["remaining_quantity"] == 3
    assert response.json()["total_price"] == 1000


def test_purchase_rejects_insufficient_stock(client):
    category_id = make_category(client)
    product_id = make_product(client, category_id).json()["id"]
    response = client.post(f"/products/{product_id}/purchase", json={"quantity": 10})
    assert response.status_code == 409


def test_search_and_summary(client):
    category_id = make_category(client)
    make_product(client, category_id)
    response = client.get("/products?search=phone")
    assert response.status_code == 200
    assert len(response.json()) == 1
    summary = client.get("/products/statistics/summary").json()
    assert summary["products_count"] == 1
    assert summary["stock_value"] == 2500
