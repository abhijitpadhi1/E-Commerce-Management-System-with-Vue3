import csv
from pathlib import Path
from typing import Any

from openpyxl import Workbook

from app.extensions import celery
from app.models import Order, User
from app.services.mail_service import send_email


EXPORT_DIR: Path = (
    Path(__file__).resolve().parents[2] / "generated_exports" / "customer_orders"
)
HEADERS = [
    "Order ID",
    "Order Date",
    "Order Status",
    "Payment Status",
    "Shipping Address",
    "Product Name",
    "Unit Price",
    "Quantity",
    "Subtotal",
    "Order Total",
]


def get_order_rows(orders: list[Order]) -> list[list[Any]]:
    rows = []

    for order in orders:
        if order.items:
            for item in order.items:
                rows.append(
                    [
                        order.id,
                        order.created_at.isoformat() if order.created_at else "",
                        order.status,
                        order.payment_status,
                        order.shipping_address,
                        item.product_name,
                        item.unit_price,
                        item.quantity,
                        item.sub_total,
                        order.total_amount,
                    ]
                )
        else:
            rows.append(
                [
                    order.id,
                    order.created_at.isoformat() if order.created_at else "",
                    order.status,
                    order.payment_status,
                    order.shipping_address,
                    "",
                    "",
                    "",
                    "",
                    order.total_amount,
                ]
            )

    return rows


def create_csv(file_path: Path, rows: list[list[Any]]) -> None:
    with file_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(HEADERS)
        writer.writerows(rows)


def create_xlsx(file_path: Path, orders: list[Order]) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Order History"

    headers = [
        "Order ID",
        "Order Date",
        "Order Status",
        "Payment Status",
        "Items",
        "Shipping Address",
        "Subtotal",
        "Discount",
        "Offer Code",
        "Order Total",
    ]

    worksheet.append(headers)

    for order in orders:
        items_text = "\n".join(
            f"{item.product_name} × {item.quantity} — ₹{item.sub_total:.2f}"
            for item in order.items
        )

        worksheet.append(
            [
                order.id,
                order.created_at.strftime("%d-%b-%Y %H:%M") if order.created_at else "",
                order.status,
                order.payment_status,
                items_text,
                order.shipping_address,
                order.subtotal,
                order.discount_amount,
                order.offer_code or "",
                order.total_amount,
            ]
        )

    # Formatting
    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    # Make headers bold
    for cell in worksheet[1]:
        cell.font = cell.font.copy(bold=True)

    # Set readable column widths
    column_widths = {
        "A": 12,
        "B": 22,
        "C": 18,
        "D": 18,
        "E": 50,
        "F": 40,
        "G": 15,
        "H": 15,
        "I": 15,
        "J": 15,
    }

    for column, width in column_widths.items():
        worksheet.column_dimensions[column].width = width

    # Wrap long product lists and addresses
    for row in worksheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = cell.alignment.copy(
                vertical="top",
                wrap_text=True,
            )

    # Format monetary columns
    for row in worksheet.iter_rows(min_row=2):
        for column in ["G", "H", "J"]:
            row[ord(column) - ord("A")].number_format = '"₹"#,##0.00'

    workbook.save(file_path)


@celery.task(bind=True)
def export_customer_order_history(
    self, customer_id: int, export_format: str = "csv"
) -> dict[str, Any]:
    """Generate the customer's order history and email it as an attachment."""

    export_format = export_format.lower()
    if export_format not in {"csv", "xlsx"}:
        raise ValueError("Unsupported export format.")

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    customer = User.query.get(customer_id)
    if not customer:
        raise ValueError("Customer account not found.")

    orders: list[Order] = (
        Order.query.filter_by(user_id=customer_id)
        .order_by(Order.created_at.desc())
        .all()
    )
    filename = f"orders_customer_{customer_id}_{self.request.id}.{export_format}"
    file_path = EXPORT_DIR / filename

    if export_format == "csv":
        rows = get_order_rows(orders)
        create_csv(file_path, rows)
    else:
        create_xlsx(file_path, orders)

    send_email(
        to_email=customer.email,
        subject="Your Order History Export",
        body=(
            "Hello,\n\n"
            "Your requested order history export is attached to this email.\n\n"
            f"Orders included: {len(orders)}\n"
            f"File format: {export_format.upper()}\n\n"
            "Thank you for shopping with us!"
        ),
        attachment_path=file_path,
    )

    return {
        "filename": file_path.name,
        "customer_id": customer_id,
        "order_count": len(orders),
        "export_format": export_format,
        "email_sent": True,
    }
