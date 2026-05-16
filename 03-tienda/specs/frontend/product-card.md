# Component: product-card

## Description
Displays information for a single product, including:
- Name
- Price
- Available stock
- Button to add to cart (if in stock)

## Suggested props
- id
- sku
- name
- price
- stock
- onAdd (callback to add to cart)

## Example usage
```jsx
<ProductCard
  id={1}
  name="Coffee"
  price={50.0}
  stock={10}
  onAdd={(id) => addToCart(id)}
/>
```

## Behavior
- If stock = 0, disable add button.
- Allow selecting quantity (optional).
