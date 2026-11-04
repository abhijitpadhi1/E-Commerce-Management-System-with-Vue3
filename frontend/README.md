# E-Commerce Management System — Frontend

The frontend is built with **Vue 3 and JavaScript**. It provides the customer shopping experience and administrator interface for product, inventory, and order management. It communicates with the Flask backend through REST APIs.

## Tech Stack

- Vue 3 and JavaScript
- Vite
- Vue Router
- Pinia
- Axios
- Bootstrap
- HTML5 and CSS3
- ESLint, Prettier, and Vitest

## Frontend Features

### Customer Interface
- Home page and product catalogue
- Customer signup and login
- Product detail pages
- Shopping cart and quantity management
- Checkout and order confirmation
- Offer/discount summary
- Mock payment interaction
- Order history and delivery confirmation
- Request order-history export in CSV or XLSX and view export status

### Administrator Interface
- Admin dashboard
- Product creation, editing, and soft deletion
- Inventory management
- Order management and fulfilment status updates

### User Experience
- Responsive layouts and reusable Vue components
- Loading, empty, success, and error states
- Notifications and form validation
- Product search and filtering
- Consistent styling and theme

## Vue Application Concepts

### Vue 3
- Composition API and `<script setup>`
- Reactive state with `ref` and `reactive`
- Computed properties and lifecycle hooks
- Component-based architecture, props, and events

### Vue Router
- Route configuration and navigation
- Protected routes and role-based navigation
- Authentication-aware route guards

### Pinia
- Authentication and current-user state
- Cart state and shared state
- Store actions and computed values

### Axios
- Centralized API configuration and REST requests
- JWT attachment through request interceptors
- Response and error handling

### Bootstrap and CSS
- Responsive layouts and utility classes
- Scoped component styles
- CSS variables for theme consistency
- Responsive product cards, forms, and dashboards

## Running the Frontend

### Prerequisites
- Node.js and npm
- Flask backend running locally on port **5001**

### Install dependencies

From the repository root:

```bash
cd frontend
npm install
```

### Start the Vite development server

```bash
npm run dev
```

Vite prints the local URL in the terminal, usually:

```text
http://localhost:5173
```

Keep the backend running while using the frontend. Ensure the frontend API configuration points to the Flask API on port `5001`.

## Frontend Learning Outcomes

- Vue application structure and reusable components
- Reactive state and Composition API
- Route guards and role-based navigation
- Shared state with Pinia
- API integration using Axios and JWTs
- Loading, success, and error states
- Form validation and user input handling
- Search, filtering, and responsive design
- Integration of customer/admin interfaces with backend workflows

## Purpose

The frontend demonstrates how a modern single-page application organizes views and state, handles user interactions, and integrates with backend services to support a complete e-commerce workflow.