# E-Commerce Management System

A full-stack e-commerce application built to explore how frontend and backend systems work together to support product management, shopping carts, orders, payments, inventory, and background processing.

The application provides separate experiences for **customers** and **administrators**. Customers can browse products, manage their cart, apply offers, place orders, simulate payments, track orders, and confirm delivery. Administrators can manage products and inventory, process orders, and review dashboard metrics.

## Features

### Customer
- Customer registration and login with JWT authentication
- Browse active products and view product details
- Add, update, and remove cart items
- Checkout with a shipping address and automatically apply the best eligible offer
- Place orders with saved item and price snapshots
- Simulate successful or failed payments
- View order history and confirm delivery of shipped orders
- Request asynchronous order-history exports in CSV or XLSX format and receive them by email
- Receive daily email reminders based on cart contents or general offers

### Administrator
- Role-protected admin access
- Create, update, and soft-delete products
- Manage inventory and stock quantities
- View and process orders; mark eligible paid orders as shipped
- View dashboard metrics for products, inventory, orders, and paid sales
- Generate monthly activity reports covering sales, orders, customers, fulfilment, and product/category performance
- Receive monthly report notifications

## Tech Stack

### Frontend
- Vue 3, JavaScript, Vite
- Vue Router, Pinia, Axios
- Bootstrap, HTML5, CSS3

### Backend
- Python, Flask, Flask-SQLAlchemy, SQLite
- Flask-JWT-Extended, Flask-CORS
- `pwdlib` with Argon2 password hashing
- `uv` for Python dependency and environment management
- Flask-Caching with Redis
- Celery and Celery Beat
- Flask-Mail with Gmail SMTP
- ReportLab and Jinja templates for PDF/HTML reports

### Development and Testing
- Git and GitHub
- ESLint, Prettier, Vitest, Pytest
- Environment variables configured through `.env`

## Background Processing and Caching

- Generate customer order exports asynchronously in CSV or XLSX and email the resulting attachment.
- Generate monthly admin activity reports and send summary notifications.
- Send daily customer email reminders through Celery Beat.
- Cache the public active-product catalogue and product-detail responses in Redis.
- Invalidate product caches after admin product changes and successful payment stock deductions.
- Keep customer-specific data such as carts and orders out of the shared product cache.

## Architecture

```text
E-Commerce-Management-System/
├── frontend/            # Vue 3 single-page application
├── backend/             # Flask REST API, database, and Celery tasks
├── README.md
├── README-frontend.md
└── README-backend.md
```

The frontend communicates with the Flask backend through REST APIs. The backend owns business logic, validation, authentication, authorization, persistence, background jobs, email delivery, and cache management.

## Running the Application Locally

### Prerequisites
- Node.js and npm
- Python version compatible with backend dependencies
- `uv`
- Redis

### 1. Configure the backend

```bash
cd backend
uv sync
```

Create/configure `backend/.env` using the project's configuration. Set the Flask/JWT and database values, Redis cache URL, Celery broker/result-backend URLs, and email/SMTP settings as required. **Do not commit `.env` or credentials.**

### 2. Start Redis

On Ubuntu:

```bash
sudo systemctl start redis-server
redis-cli ping
```

Expected response: `PONG`.

### 3. Start the Flask API

In a terminal:

```bash
cd backend
uv run main.py
```

The backend runs locally on port **5001**.

### 4. Start the Celery worker

In a second terminal:

```bash
cd backend
uv run celery -A celery_app:celery worker --loglevel=INFO
```

The worker executes queued tasks such as order exports and report generation.

### 5. Start Celery Beat

In a third terminal:

```bash
cd backend
uv run celery -A celery_app:celery beat --loglevel=INFO
```

Beat publishes scheduled tasks, including daily reminders and the monthly admin report. Keep both worker and Beat running for background and scheduled jobs.

### 6. Start the frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite prints the local URL, usually `http://localhost:5173`. Ensure the frontend API configuration points to the Flask API on port `5001`.

### Local services overview

| Service | Purpose | Command |
|---|---|---|
| Redis | Cache and Celery broker/backend | `sudo systemctl start redis-server` |
| Flask | REST API | `cd backend && uv run main.py` |
| Celery worker | Executes background tasks | `cd backend && uv run celery -A celery_app:celery worker --loglevel=INFO` |
| Celery Beat | Schedules recurring tasks | `cd backend && uv run celery -A celery_app:celery beat --loglevel=INFO` |
| Vite | Frontend dev server | `cd frontend && npm run dev` |

Run each command in its own terminal. Configure `.env` before starting services.

## Project Learning Approach

1. Project setup and architecture
2. Database design and models
3. Authentication and role-based authorization
4. Product management and catalogue
5. Shopping cart and checkout
6. Offers and order totals
7. Mock payments and inventory consistency
8. Order fulfilment and admin dashboard
9. Asynchronous exports and email delivery
10. Scheduled reports and customer reminders
11. Redis caching and cache invalidation
12. End-to-end testing and refinement

## Purpose

This project is a practical learning experience in full-stack development and application integration. It explores API design, relational data, authentication, asynchronous processing, scheduled tasks, caching, and a realistic business workflow.