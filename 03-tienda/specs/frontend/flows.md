# Main flows for the Frontend — MiniMarket

## 1. View products
- **Actor:** Customer
- **Flow:**
  1. The customer accesses the products page.
  2. The frontend requests `GET /products` from the backend.
  3. The list of products is displayed with name, price, and stock.

## 2. Create order
- **Actor:** Customer
- **Flow:**
  1. The customer selects products and quantities from the list.
  2. Enters their email.
  3. The frontend sends a `POST /orders` with the email and selected items.
  4. If the response is 201, confirmation and order details are shown.
  5. If there is an error (insufficient stock, product does not exist, etc.), an error message is shown.

## 3. View orders
- **Actor:** Customer/Admin
- **Flow:**
  1. The user accesses the orders page.
  2. The frontend requests `GET /orders` from the backend.
  3. The list of orders is displayed with their items, totals, and date.

---

# Suggested structure for the Frontend

- **Products page**
  - Lists all products
  - Allows selecting quantity and adding to cart

- **Shopping cart**
  - Shows selected products and quantities
  - Allows modifying quantities or removing products
  - Button to create order

- **Order form**
  - Field for email
  - Button to confirm order
  - Shows confirmation or errors

- **Orders page**
  - Lists all orders placed
  - Shows details: products, quantities, totals, date

---

# Notes
- The frontend can be a simple SPA (React, Vue, etc.) or classic HTML.
- Use fetch/AJAX to consume the API.
- Validate data before sending orders.
- Show clear success/error messages.
