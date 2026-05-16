# Frontend Architecture

## Goal

Frontend application for ecommerce store.

The frontend consumes existing microservices:
- products-service
- orders-service

The architecture should be:
- simple
- scalable
- component driven
- easy to maintain
- AI friendly

---

# Stack

- React
- TypeScript
- Vite
- TailwindCSS

---

# Folder Structure

src/
│
├── api/
├── components/
├── hooks/
├── pages/
├── types/
├── services/
├── utils/
└── layouts/

---

# Responsibilities

## pages/

Page components should:
- orchestrate UI
- call hooks
- manage page layout

Pages should NOT:
- contain business logic
- make direct fetch calls

---

## components/

Reusable UI components.

Examples:
- ProductCard
- ProductGrid
- Navbar
- Button

Components should:
- be reusable
- receive props
- avoid API calls

---

## hooks/

Hooks contain:
- API logic
- async state
- reusable business logic

Examples:
- useProducts
- useOrders

---

## api/

API communication layer.

Responsibilities:
- fetch requests
- response parsing
- error handling

Examples:
- productsApi.ts
- ordersApi.ts

---

## types/

Shared TypeScript types.

Examples:
- Product
- Order
- ApiError

---

# State Management

Initial state management strategy:
- useState
- useEffect
- custom hooks

Avoid:
- Redux
- complex global state

---

# API Rules

- Frontend consumes REST APIs
- JSON only
- async/await required
- no direct fetch inside components

---

# Component Rules

- Functional components only
- PascalCase for component names
- One component per file

---

# Styling Rules

- TailwindCSS only
- mobile first
- reusable utility classes

Avoid:
- inline styles
- duplicated styles

---

# Error Handling

Each async flow should support:
- loading
- success
- error
- empty state

---

# AI Rules

- Reuse existing components
- Reuse shared types
- Avoid duplicated API logic
- Follow folder structure
- Keep components small

---

# Future Improvements

Possible future additions:
- authentication
- React Query
- tests
- Storybook
- design system