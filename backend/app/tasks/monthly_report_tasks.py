from datetime import datetime, timezone
from pathlib import Path
from calendar import monthrange
from collections import defaultdict
from decimal import Decimal
from sqlalchemy import func
import logging

from app.extensions import db, celery
from app.models import Order, OrderItem, Payment, Product
from app.services.google_chat import send_google_chat_message
from app.services.monthly_report import (
    build_monthly_report_message,
    build_monthly_report_html,
    build_monthly_report_pdf,
)

logger = logging.getLogger(__name__)


def get_previous_month_range() -> tuple[datetime, datetime]:
    """Return the start and end of the previous calendar month. The end is exclusive."""
    now: datetime = datetime.now(timezone.utc)
    first_day_this_month: datetime = now.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    last_day_previous_month: datetime = first_day_this_month.replace(day=1)

    if first_day_this_month.month == 1:
        start: datetime = first_day_this_month.replace(
            year=first_day_this_month.year - 1, month=12
        )
    else:
        start: datetime = first_day_this_month.replace(
            month=first_day_this_month.month - 1
        )

    return start, first_day_this_month


def money(value: Decimal | None) -> float:
    """Convert Decimal/None to a JSON-friendly numeric value."""
    return float(value or Decimal("0.00"))


def process_monthly_admin_report(report_data: dict) -> dict:
    """
    Generate the HTML and PDF reports, then send the monthly summary to the configured Google Chat space.

    Args:
        report_data: The monthly report data returned by generate_monthly_admin_report().

    Returns:
        A dictionary containing generated file paths and notification status.
    """

    # 1. Generate the HTML report
    html_content = build_monthly_report_html(report_data)

    # 2. Generate the PDF report
    pdf_bytes = build_monthly_report_pdf(report_data)

    # 3. Create the PDF output directory
    output_dir = Path(__file__).resolve().parents[2] / "generated_exports" / "pdfs"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 4. Build a filename using the report month
    report_period = report_data["report_period"]
    pdf_filename = f"monthly_admin_report_{report_period['start'][:7]}.pdf"

    # 5. Save the PDF
    pdf_path = output_dir / pdf_filename
    pdf_path.write_bytes(pdf_bytes)

    # 6. Build and send the Google Chat message
    chat_message = build_monthly_report_message(report_data)
    notification_sent = send_google_chat_message(chat_message)

    if not notification_sent:
        logger.error(
            "Monthly report was generated, but Google Chat notification failed."
        )

    # 7. Return processing results
    return {
        "pdf_path": str(pdf_path),
        "html_generated": bool(html_content),
        "notification_sent": notification_sent,
    }


@celery.task
def generate_monthly_admin_report() -> dict:
    """Generate a structured activity summary for the previous calendar month."""
    start_date, end_date = get_previous_month_range()

    # ---------------------------------------------------------
    # 1. Successful payments during the reporting month
    # ---------------------------------------------------------
    successful_payments: list = (
        db.session.query(Payment, Order)
        .join(Order, Payment.order_id == Order.id)
        .filter(
            Payment.payment_status == "SUCCESS",
            Payment.created_at >= start_date,
            Payment.created_at < end_date,
        )
        .all()
    )

    paid_sales: Decimal = sum(
        (payment.amount or Decimal("0.00")) for payment, order in successful_payments
    )
    paid_order_ids: set[int] = {order.id for payment, order in successful_payments}
    buying_customer_ids: set[int] = {
        order.user_id for payment, order in successful_payments
    }

    # ---------------------------------------------------------
    # 2. Orders created during the reporting month
    # ---------------------------------------------------------
    orders_created: Query = Order.query.filter(
        Order.created_at >= start_date,
        Order.created_at < end_date,
    )

    total_orders: int = orders_created.count()

    order_status_counts: list = (
        db.session.query(Order.status, func.count(Order.id))
        .filter(
            Order.created_at >= start_date,
            Order.created_at < end_date,
        )
        .group_by(Order.status)
        .all()
    )
    order_status_summary: dict[str, int] = {
        status: count for status, count in order_status_counts
    }

    # ---------------------------------------------------------
    # 3. Shipping and delivery activity during the month
    # ---------------------------------------------------------
    shipped_orders: int = Order.query.filter(
        Order.shiped_at >= start_date,
        Order.shiped_at < end_date,
    ).count()

    delivered_orders: int = Order.query.filter(
        Order.delivered_at >= start_date,
        Order.delivered_at < end_date,
    ).count()

    # ---------------------------------------------------------
    # 4. Product and category performance
    #    Use OrderItem purchase-time snapshots for revenue.
    # ---------------------------------------------------------
    product_summary: dict[int, dict] = defaultdict(
        lambda: {
            "product_name": "",
            "quantity_sold": 0,
            "revenue": Decimal("0.00"),
        }
    )

    category_summary: dict[str, dict] = defaultdict(
        lambda: {
            "category": "",
            "quantity_sold": 0,
            "revenue": Decimal("0.00"),
        }
    )

    if paid_order_ids:
        paid_order_items: list[tuple[OrderItem, Product]] = (
            db.session.query(OrderItem, Product)
            .join(Product, OrderItem.product_id == Product.id)
            .filter(OrderItem.order_id.in_(paid_order_ids))
            .all()
        )

        for item, product in paid_order_items:
            product_data: dict[str, Any] = product_summary[item.product_id]
            product_data["product_name"] = item.product_name
            product_data["quantity_sold"] += item.quantity
            product_data["revenue"] += item.sub_total

            category_data: dict[str, Any] = category_summary[product.category]
            category_data["category"] = product.category
            category_data["quantity_sold"] += item.quantity
            category_data["revenue"] += item.sub_total

    # ---------------------------------------------------------
    # 5. Sort product/category results
    # ---------------------------------------------------------
    top_products: list[dict[str, Any]] = sorted(
        product_summary.values(),
        key=lambda item: item["quantity_sold"],
        reverse=True,
    )

    category_performance: list[dict[str, Any]] = sorted(
        category_summary.values(),
        key=lambda item: item["revenue"],
        reverse=True,
    )

    # ---------------------------------------------------------
    # 6. Return JSON-friendly report data
    # ---------------------------------------------------------
    report_data: dict[str, Any] = {
        "report_period": {
            "start": start_date.date().isoformat(),
            "end": (end_date.date()).isoformat(),
            "description": "Previous calendar month",
        },
        "executive_summary": {
            "paid_sales": money(paid_sales),
            "total_orders_created": total_orders,
            "unique_buying_customers": len(buying_customer_ids),
            "successful_payments": len(successful_payments),
        },
        "order_status_summary": order_status_summary,
        "fulfillment_summary": {
            "orders_shipped_during_month": shipped_orders,
            "orders_delivered_during_month": delivered_orders,
        },
        "top_products": [
            {
                "product_name": item["product_name"],
                "quantity_sold": item["quantity_sold"],
                "revenue": money(item["revenue"]),
            }
            for item in top_products
        ],
        "category_performance": [
            {
                "category": item["category"],
                "quantity_sold": item["quantity_sold"],
                "revenue": money(item["revenue"]),
            }
            for item in category_performance
        ],
    }

    processing_result: dict[str, Any] = process_monthly_admin_report(report_data)

    return {**report_data, **processing_result}
