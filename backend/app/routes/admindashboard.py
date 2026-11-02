from flask import Blueprint, jsonify, Response
from sqlalchemy import func

from app.extensions import db
from app.models import Product, Order
from app.utils.decorators import role_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.get("/stats")
@role_required("ADMIN")
def get_admin_dashboard() -> tuple[Response, int]:
    total_products: int = Product.query.count()

    active_products: int = Product.query.filter_by(is_active=True).count()

    low_stock_products: int = Product.query.filter(
        Product.is_active.is_(True),
        Product.stock > 0,
        Product.stock <= 5,
    ).count()

    out_of_stock_products: int = Product.query.filter(
        Product.is_active.is_(True),
        Product.stock == 0,
    ).count()

    total_orders: int = Order.query.count()

    pending_payment_orders: int = Order.query.filter_by(
        payment_status="PENDING"
    ).count()

    processing_orders: int = Order.query.filter_by(
        status="PROCESSING",
        payment_status="PAID",
    ).count()

    shipped_orders = Order.query.filter_by(status="SHIPPED").count()

    delivered_orders = Order.query.filter_by(status="DELIVERED").count()

    total_sales = (
        db.session.query(func.coalesce(func.sum(Order.total_amount), 0))
        .filter(Order.payment_status == "PAID")
        .scalar()
    )

    return (
        jsonify(
            {
                "dashboard": {
                    "total_products": total_products,
                    "active_products": active_products,
                    "low_stock_products": low_stock_products,
                    "out_of_stock_products": out_of_stock_products,
                    "total_orders": total_orders,
                    "pending_payment_orders": pending_payment_orders,
                    "processing_orders": processing_orders,
                    "shipped_orders": shipped_orders,
                    "delivered_orders": delivered_orders,
                    "total_sales": str(total_sales),
                }
            }
        ),
        200,
    )
