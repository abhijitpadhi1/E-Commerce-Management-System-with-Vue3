# E-Commerce Management System — Frontend

The frontend is built using **Vue 3 and JavaScript**. It provides the customer-facing shopping experience and the administrator interface for managing products, inventory, and orders.

The frontend communicates with the Flask backend through REST APIs.

## Tech Stack

- Vue 3
- JavaScript
- Vite
- Vue Router
- Pinia
- Axios
- Bootstrap
- HTML5
- CSS3
- ESLint
- Prettier
- Vitest

## Frontend Features

### Customer Interface
- Home page
- Customer signup and login
- Product catalogue
- Product details
- Shopping cart
- Checkout
- Order confirmation
- Mock payment interaction
- Order history
- Delivery confirmation

### Administrator Interface
- Admin dashboard
- Product management
- Inventory management
- Order management
- Order status updates

### UI and User Experience
- Responsive layouts
- Reusable Vue components
- Loading states
- Empty states
- Error handling
- Notifications
- Form validation
- Search and filtering
- Consistent application theme

## Vue Application Concepts Used

### Vue 3
- Composition API
- `<script setup>`
- Reactive state using `ref` and `reactive`
- Computed properties
- Lifecycle hooks
- Component-based architecture
- Props and component events

### Vue Router
- Route configuration
- Navigation between views
- Protected routes
- Role-based navigation
- Authentication-aware route guards

### Pinia
- Authentication state
- Current-user state
- Cart state
- Shared state across components
- Store actions and computed values

### Axios
- Centralized API configuration
- REST API requests
- JWT token attachment through request interceptors
- Handling API responses and errors

### Bootstrap and CSS
- Responsive layouts
- Bootstrap utility classes and components
- Scoped component styles
- CSS variables for theme consistency
- Responsive product cards, forms, and dashboards

## What We Learned

Through frontend development, we learned:

- How to structure a Vue application
- How to build reusable components
- How to manage reactive state
- How to use the Composition API
- How to configure and use Vue Router
- How to protect routes based on authentication and user roles
- How to manage shared state with Pinia
- How to communicate with a backend using Axios
- How to attach JWT tokens to protected requests
- How to handle loading, success, and error states
- How to build forms and validate user input
- How to implement product search and filtering
- How to create responsive interfaces using Bootstrap and CSS
- How to maintain consistent styling through CSS variables
- How to build customer and administrator interfaces within one application
- How to integrate frontend workflows with backend business logic

## Running the Frontend

From the `frontend/` directory, install dependencies and start the development server:

```bash
npm install
npm run dev
```

The frontend runs locally using Vite. The backend API is configured to run on port `5001`.

## Purpose

The frontend was developed to understand how a modern single-page application is structured, how state is managed, and how user interactions are connected to backend services.