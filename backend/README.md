# E-Commerce Management System — Backend

The backend is built with **Python and Flask**. It exposes REST APIs for authentication, products, carts, checkout, offers, orders, mock payments, inventory, and admin metrics. It also manages background tasks, scheduled jobs, email delivery, report generation, and Redis caching.

## Tech Stack

- Python, Flask, Flask-SQLAlchemy, SQLite
- Flask-JWT-Extended, Flask-CORS
- `pwdlib` with Argon2 password hashing
- `uv` for dependency and environment management
- Flask-Caching with Redis
- Celery and Celery Beat
- Flask-Mail with Gmail SMTP
- ReportLab and Jinja templates for PDF/HTML reports
- Python dotenv and Pytest

## Backend Features

### Authentication and Authorization
- Customer signup and admin/customer login
- Argon2 password hashing and JWT authentication
- Role-based access control and protected endpoints
- Active-user validation and resource ownership checks

### Product Management and Redis Cache
- Create, retrieve, update, and soft-delete products
- Public catalogue and product-detail endpoints for active products
- Admin listing can include inactive products
- Cache active catalogue and product-detail responses in Redis
- Invalidate catalogue and relevant detail caches after admin product changes
- Invalidate catalogue and affected detail caches after successful payment stock deductions
- Cache errors are logged without disrupting core database operations

### Shopping Cart and Offers
- Create/retrieve a customer's cart; add, update, remove, and clear items
- Validate product availability and stock
- Evaluate percentage, fixed-amount, category, quantity-based, and buy-X-get-Y-free offers
- Select the best eligible offer, do not stack discounts, and cap discount at eligible subtotal

### Orders and Checkout
- Create orders from cart contents
- Validate shipping address, product availability, and stock
- Persist subtotal, discount, offer code, and final order total
- Store order-item name and unit-price snapshots
- Retrieve customer order history and admin order listings

### Mock Payments and Inventory
- Simulate successful and failed payments
- Store payment records and mock transaction references
- Deduct stock only after successful payment
- Revalidate stock before deduction and prevent repeated processing
- Update payment and order states consistently

### Order Fulfilment and Dashboard
- Admins mark eligible paid orders as shipped; customers confirm delivery
- Track order lifecycle timestamps
- Show product, inventory, order-status, paid-sales, low-stock, and out-of-stock metrics
- Paid sales are not presented as profit

### Celery Background Tasks
- Generate customer order-history exports asynchronously in CSV or XLSX
- Email export files to customers
- Generate monthly admin activity reports with sales, orders, customers, fulfilment, and product/category summaries
- Render monthly reports as HTML/PDF and send a summary notification
- Send daily customer email reminders based on cart contents or general offers
- Schedule recurring tasks through Celery Beat using the configured timezone

## Database

The application uses SQLite with Flask-SQLAlchemy. Main models:

- `User`
- `Product`
- `Cart`
- `CartItem`
- `Order`
- `OrderItem`
- `Payment`

Relationships, foreign keys, uniqueness constraints, validation, and transaction handling support data consistency. Order items preserve product-name and unit-price snapshots for historical accuracy.

## Running the Backend

### Prerequisites
- Python version compatible with project dependencies
- `uv`
- Redis server
- Configured backend `.env`

### 1. Install dependencies

From the repository root:

```bash
cd backend
uv sync
```

### 2. Configure environment

Create/configure `.env` using the project's existing configuration. Set Flask/JWT and database values, Redis cache URL, Celery broker/result-backend URLs, and email/SMTP settings as required. Keep credentials and `.env` out of version control.

### 3. Start Redis

On Ubuntu:

```bash
sudo systemctl start redis-server
redis-cli ping
```

Expected response: `PONG`.

### 4. Run the Flask API

```bash
uv run main.py
```

The API runs locally on port **5001**.

### 5. Run the Celery worker

In a separate terminal, from `backend/`:

```bash
uv run celery -A celery_app:celery worker --loglevel=INFO
```

### 6. Run Celery Beat

In another terminal, from `backend/`:

```bash
uv run celery -A celery_app:celery beat --loglevel=INFO
```

The worker executes queued tasks; Beat publishes scheduled tasks. Keep both running for background processing and scheduled email/report workflows.

## Backend Learning Outcomes

- Flask application-factory architecture and REST API design
- SQLAlchemy models, relationships, and transactions
- Authentication, JWTs, role-based authorization, and ownership checks
- Input validation and HTTP status handling
- Checkout, offers, payment, and inventory business logic
- Asynchronous task processing and scheduled jobs
- Email delivery and report generation
- Redis caching and cache invalidation
- Configuration/secrets management and Pytest-based API testing

## Purpose

The backend demonstrates how business rules, authentication, persistence, asynchronous processing, caching, and API design work together to support a full-stack application.