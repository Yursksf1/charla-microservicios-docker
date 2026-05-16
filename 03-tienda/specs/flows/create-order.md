# Flow: Create Order

## Actor
Customer (via frontend)

## Steps
1. The customer selects products and quantities from the products list.
2. The customer enters their email address.
3. The frontend sends a POST request to `/orders` with:
	- `customer_email`: string
	- `items`: array of `{ product_id: int, qty: int }`
4. The orders service:
	- Validates each product by requesting `/products/{id}` from the products service.
	- If any product does not exist or is unavailable, returns an error (404 or 502).
	- Calculates the total using the current price from the products service.
	- Saves the order and its items in the database.
	- Publishes an `order.created` event to RabbitMQ.
5. The API responds with 201 Created and the order details (including enriched items and total).
6. The frontend displays a confirmation or error message to the customer.

## Error Scenarios
- If a product does not exist: 404 error.
- If the products service is unavailable: 503 error.
- If the order is saved but the event cannot be published: order is created, but a warning is logged.
