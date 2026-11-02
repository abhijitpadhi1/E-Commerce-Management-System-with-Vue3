# E-Commerce Management System — Backend

The backend is built using **Python and Flask**. It provides REST APIs for authentication, product management, shopping carts, checkout, orders, mock payments, inventory, and dashboard metrics.

The backend handles business logic, data validation, authentication, authorization, and database operations.

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Flask-JWT-Extended
- Flask-CORS
- `pwdlib` with Argon2 password hashing
- `uv` for dependency and environment management
- Python dotenv for environment variables
- Pytest for testing

## Backend Features

### Authentication and Authorization
- Customer signup and login
- Admin login
- Password hashing
- JWT-based authentication
- Role-based access control
- Protected endpoints
- Active-user validation

### Product Management
- Create products
- Retrieve active products
- Retrieve individual product details
- Update product information
- Soft-delete products
- Admin product listing, including inactive products

### Shopping Cart
- Create or retrieve a customer cart
- Add products to the cart
- Update item quantities
- Remove cart items
- Clear the cart
- Validate product availability and stock

### Orders and Checkout
- Create orders from cart contents
- Validate shipping address and product availability
- Store order-item snapshots
- Calculate order totals
- Retrieve customer order history
- Retrieve all orders for administrators

### Mock Payments
- Simulate successful and failed payments
- Store payment records
- Update order payment status
- Generate mock transaction references
- Prevent repeated payment processing

### Inventory Management
- Deduct stock after successful payment
- Recheck stock before payment processing
- Prevent overselling
- Update product stock
- Track low-stock and out-of-stock products

### Order Fulfilment
- Allow administrators to mark paid orders as shipped
- Allow customers to confirm delivery
- Track order lifecycle timestamps

### Admin Dashboard
- Product and inventory metrics
- Order status metrics
- Total paid sales
- Low-stock and out-of-stock counts

## Database

The application uses SQLite with Flask-SQLAlchemy.

The main database models are:

- `User`
- `Product`
- `Cart`
- `CartItem`
- `Order`
- `OrderItem`
- `Payment`

The database design uses relationships, foreign keys, uniqueness constraints, and validation rules to maintain data consistency.

Order items store product-name and unit-price snapshots so that historical orders remain accurate even if product details change later.

## What We Learned

Through backend development, we learned:

- How to structure a Flask application using the application-factory pattern
- How to organize routes, models, extensions, configuration, and utilities
- How to design relational database schemas
- How to use SQLAlchemy models and relationships
- How to implement RESTful API endpoints
- How to validate request data and return appropriate HTTP status codes
- How to hash passwords securely
- How JWT authentication works
- How to implement role-based authorization
- How to protect resources using ownership checks
- How to implement CRUD operations
- How to handle database transactions and commits
- How to design checkout and payment workflows
- How to maintain inventory consistency
- How to use environment variables for configuration and secrets
- How to seed initial administrator and dummy product data
- How to test API behavior and authorization using Pytest

## Running the Backend

From the `backend/` directory, install dependencies using `uv`, configure the required environment variables in `.env`, and run:

```bash
uv run main.py
```

The backend runs locally on port `5001`.

## Purpose

The backend was developed to understand how business rules, authentication, data persistence, and API design work together to support a real-world application workflow.