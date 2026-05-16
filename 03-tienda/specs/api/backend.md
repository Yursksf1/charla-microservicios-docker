
# API Specification — MiniMarket Backend

## Service: Products

### List products
- **GET** `/products`
- **Response:**
  - 200 OK
  - JSON: List of products
  - Example:
    ```json
    [
      {"id": 1, "sku": "A1", "name": "Coffee", "price": 50.0, "stock": 10},
      {"id": 2, "sku": "B2", "name": "Tea", "price": 30.0, "stock": 5}
    ]
    ```

### Get product by ID
- **GET** `/products/{id}`
- **Response:**
  - 200 OK
  - JSON: Product
  - 404 if not found
  - Example:
    ```json
    {"id": 1, "sku": "A1", "name": "Coffee", "price": 50.0, "stock": 10}
    ```

### Create product
- **POST** `/products`
- **Body:**
  - JSON: {"sku": str, "name": str, "price": float, "stock": int}
- **Response:**
  - 201 Created
  - JSON: Created product

---

## Service: Orders

### Create order
- **POST** `/orders`
- **Body:**
  - JSON: {"customer_email": str, "items": [{"product_id": int, "qty": int}]}
- **Response:**
  - 201 Created
  - JSON: Created order (with enriched items and total)
  - Example:
    ```json
    {
      "id": 1,
      "customer_email": "customer@example.com",
      "total": 100.0,
      "created_at": "2024-05-15T12:00:00",
      "items": [
        {"product_id": 1, "name": "Coffee", "unit_price": 50.0, "qty": 2, "subtotal": 100.0}
      ]
    }
    ```

### List orders
- **GET** `/orders`
- **Response:**
  - 200 OK
  - JSON: List of orders (with items)

---

## Notes
- All endpoints return JSON.
- Common errors: 404 (not found), 400 (invalid request), 503 (service unavailable).
- The orders service validates products against the products service.
- The `order.created` event is published to RabbitMQ after order creation.
