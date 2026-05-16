# Page: products-page

## Description
Displays the list of products available for sale.

## Main elements
- Title: "Products"
- List of `product-card` for each product
- Button to go to the cart

## Flow
1. On load, requests `GET /products` from the backend.
2. Displays each product using the `product-card` component.
3. Allows adding products to the cart.
4. Button to navigate to the shopping cart.

## Notes
- Show a message if there are no products.
- Handle loading and error states.
