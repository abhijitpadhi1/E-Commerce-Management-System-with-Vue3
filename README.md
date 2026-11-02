# E-Commerce Management System

A full-stack mini e-commerce application built to explore how frontend and backend systems work together to support product management, shopping carts, orders, payments, and inventory.

The application includes separate experiences for **customers** and **administrators**. Customers can browse products, manage their cart, place orders, simulate payments, and confirm delivery. Administrators can manage products, monitor inventory, and process orders.

## Tech Stack

### Frontend
- Vue 3
- JavaScript
- Vite
- Vue Router
- Pinia
- Axios
- Bootstrap
- HTML5 and CSS3

### Backend
- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Flask-JWT-Extended
- Flask-CORS
- `pwdlib` with Argon2 password hashing
- `uv` for Python dependency management

### Development and Testing
- Git and GitHub
- ESLint
- Prettier
- Vitest
- Pytest
- Environment variables using `.env`

## Application Features

### Customer
- Customer registration and login
- Browse and view product details
- Add, update, and remove cart items
- Checkout with a shipping address
- Place orders
- Simulate payment using a mock payment system
- View order history
- Confirm receipt of shipped orders

### Administrator
- Admin login
- Create and manage products
- Soft-delete products from the catalogue
- Manage inventory and stock quantities
- View order details
- Mark paid orders as shipped
- View dashboard metrics for products, inventory, and orders

## What We Learned

Developing this application helped us understand how to design and build a full-stack system from the ground up.

- How frontend and backend applications communicate through REST APIs
- How to organize a project into separate frontend and backend layers
- How to design relational database tables and relationships
- How authentication and role-based authorization work
- How to manage application state using Pinia
- How to handle asynchronous API requests and application errors
- How to implement CRUD operations
- How to manage cart, checkout, order, and payment workflows
- How to maintain inventory consistency and prevent overselling
- How to preserve order-item snapshots for historical accuracy
- How to use environment variables and protect sensitive configuration
- How to build reusable components and maintain consistent UI styling
- How to validate inputs and test application workflows

## Project Learning Approach

The application was developed in stages:

1. Project setup
2. Database design
3. Authentication
4. Product management
5. Product catalogue
6. Shopping cart
7. Checkout and order creation
8. Mock payment
9. Order management
10. Inventory management
11. Admin dashboard
12. UI refinement and testing

## Purpose

This project was developed as a practical learning experience to understand the architecture, implementation, and integration of a full-stack web application. It focuses on learning core development concepts through a realistic business workflow.