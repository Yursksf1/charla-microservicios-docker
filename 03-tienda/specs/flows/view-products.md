# Flow: View Products

## Actor
Customer (via frontend)

## Steps
1. The customer navigates to the products page in the frontend.
2. The frontend sends a GET request to `/products`.
3. The products service retrieves all products from the database.
4. The API responds with a list of products, each including:
	- id, sku, name, price, stock
5. The frontend displays the list of products with their details.

## Error Scenarios
- If the products service is unavailable: 503 error.
- If there are no products: show an empty state message.
