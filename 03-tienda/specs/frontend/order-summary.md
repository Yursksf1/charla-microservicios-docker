# Component: order-summary

## Description
Displays the summary of an order, including:
- Customer email
- Creation date
- List of products (name, quantity, unit price, subtotal)
- Order total

## Suggested props
- id
- customer_email
- created_at
- items (array of products)
- total

## Example usage
```jsx
<OrderSummary
  id={1}
  customer_email="customer@example.com"
  created_at="2024-05-15T12:00:00"
  total={100.0}
  items={[
    { product_id: 1, name: "Coffee", unit_price: 50.0, qty: 2, subtotal: 100.0 }
  ]}
/>
```

## Behavior
- Show all products in the order.
- Show total and date in a readable format.
