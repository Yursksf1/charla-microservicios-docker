# Business Rules — MiniMarket

## Products
- Each product has a unique SKU, name, price (>= 0), and stock (>= 0).
- Products can only be created with non-negative price and stock.
- Product stock is not decremented when an order is created (handled separately, e.g., by a worker or manually).
- Products cannot be deleted if referenced by any order (future-proofing).

## Orders
- An order must have a valid customer email and at least one item.
- Each item in an order must reference a valid product (checked via products service).
- The quantity for each item must be > 0.
- The order total is calculated as the sum of (unit_price * qty) for all items, using the current price from the products service.
- Orders are saved only if all products are valid and available.
- After saving, an 'order.created' event is published to RabbitMQ.
- Orders cannot be modified or deleted once created (immutable for simplicity).

## Error Handling
- If a product does not exist or is unavailable, the order is rejected.
- If the products service is unavailable, the order is rejected with a 503 error.
- If any database or messaging error occurs, the operation is aborted and an error is returned.

## Notes
- All business logic for validation and calculation is handled in the orders service, not in the frontend.
- The products service is the single source of truth for product data.
