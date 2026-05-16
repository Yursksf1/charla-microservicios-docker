    # Page: order-page

## Description
Displays the details of a created order.

## Main elements
- Title: "Order Details"
- `order-summary` component showing the order details
- Button to go back to products page    
## Flow
1. After creating an order, the frontend navigates to this page.
2. The order details are passed as props to the `order-summary` component.
3. The user can review the order details and click the button to return to the products page.
## Notes
- Show a message if there was an error creating the order.
- Ensure the order details are displayed in a clear and readable format.
