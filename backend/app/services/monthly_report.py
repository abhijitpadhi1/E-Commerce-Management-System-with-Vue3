from io import BytesIO
from datetime import datetime, timedelta
from flask import render_template
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)


def format_currency(value: float | int | None) -> str:
    """Format a numeric amount as Indian Rupees."""
    return f"INR {float(value or 0):,.2f}"


def format_report_period(start: str, end_exclusive: str) -> str:
    """
    Convert an exclusive end date into a human-readable period.

    Example:
    2026-10-01 to 2026-11-01 -> October 1–31, 2026
    """
    start_date = datetime.fromisoformat(start).date()
    end_date = datetime.fromisoformat(end_exclusive).date()

    # The report's end date is exclusive, so subtract one day.
    last_day = end_date - timedelta(days=1)

    if start_date.year == last_day.year and start_date.month == last_day.month:
        return f"{start_date.strftime('%B')} {start_date.day}–{last_day.day}, {start_date.year}"

    return f"{start_date.strftime('%b %d, %Y')} – {last_day.strftime('%b %d, %Y')}"


def build_monthly_report_pdf(report_data: dict) -> bytes:
    """
    Build a monthly admin report PDF from the dictionary
    returned by generate_monthly_admin_report().
    """
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Monthly Admin Activity Report",
        author="E-Commerce Management System",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#183153"),
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#5B6573"),
        spaceAfter=18,
    )

    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#183153"),
        spaceBefore=12,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
    )

    story = []

    # ---------------------------------------------------------
    # 1. Report title and period
    # ---------------------------------------------------------
    period = format_report_period(
        report_data["report_period"]["start"],
        report_data["report_period"]["end"],
    )

    story.append(Paragraph("Monthly Admin Activity Report", title_style))
    story.append(Paragraph(period, subtitle_style))

    # ---------------------------------------------------------
    # 2. Executive summary
    # ---------------------------------------------------------
    summary = report_data["executive_summary"]

    story.append(Paragraph("Executive Summary", section_style))

    summary_data = [
        ["Paid Sales", "Orders Created", "Buying Customers", "Successful Payments"],
        [
            format_currency(summary.get("paid_sales")),
            str(summary.get("total_orders_created", 0)),
            str(summary.get("unique_buying_customers", 0)),
            str(summary.get("successful_payments", 0)),
        ],
    ]

    summary_table = Table(summary_data, colWidths=[42 * mm, 42 * mm, 42 * mm, 42 * mm])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#183153")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#EEF3F8")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D4DCE5")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
            ]
        )
    )

    story.append(summary_table)
    story.append(Spacer(1, 5 * mm))

    # ---------------------------------------------------------
    # 3. Order status summary
    # ---------------------------------------------------------
    story.append(Paragraph("Order Status Summary", section_style))
    status_summary = report_data.get("order_status_summary", {})
    status_data = [["Order Status", "Number of Orders"]]
    if status_summary:
        for status, count in sorted(status_summary.items()):
            status_data.append([str(status).replace("_", " ").title(), str(count)])
    else:
        status_data.append(["No orders recorded", "0"])

    status_table = Table(status_data, colWidths=[90 * mm, 50 * mm], repeatRows=1)
    status_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E3EAF2")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8D1DC")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F7F9FB")],
                ),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(status_table)

    # ---------------------------------------------------------
    # 4. Fulfillment activity
    # ---------------------------------------------------------
    story.append(Paragraph("Fulfillment Activity", section_style))
    fulfillment = report_data.get("fulfillment_summary", {})
    fulfillment_data = [
        ["Activity", "Orders"],
        [
            "Orders shipped during the month",
            str(fulfillment.get("orders_shipped_during_month", 0)),
        ],
        [
            "Orders delivered during the month",
            str(fulfillment.get("orders_delivered_during_month", 0)),
        ],
    ]
    fulfillment_table = Table(
        fulfillment_data, colWidths=[90 * mm, 50 * mm], repeatRows=1
    )
    fulfillment_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E3EAF2")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8D1DC")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F7F9FB")],
                ),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(fulfillment_table)

    # ---------------------------------------------------------
    # 5. Top products
    # ---------------------------------------------------------
    story.append(Paragraph("Top Products by Quantity Sold", section_style))
    products = report_data.get("top_products", [])
    product_data = [["Product", "Quantity Sold", "Revenue"]]
    if products:
        for item in products[:10]:
            product_data.append(
                [
                    Paragraph(str(item["product_name"]), normal_style),
                    str(item["quantity_sold"]),
                    format_currency(item["revenue"]),
                ]
            )
    else:
        product_data.append(["No product sales recorded", "0", format_currency(0)])

    product_table = Table(
        product_data, colWidths=[78 * mm, 32 * mm, 40 * mm], repeatRows=1
    )
    product_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#183153")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8D1DC")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F7F9FB")],
                ),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(product_table)

    # ---------------------------------------------------------
    # 6. Category performance
    # ---------------------------------------------------------
    story.append(Paragraph("Category Performance", section_style))
    categories = report_data.get("category_performance", [])
    category_data = [["Category", "Quantity Sold", "Revenue"]]
    if categories:
        for item in categories:
            category_data.append(
                [
                    Paragraph(str(item["category"]), normal_style),
                    str(item["quantity_sold"]),
                    format_currency(item["revenue"]),
                ]
            )
    else:
        category_data.append(["No category sales recorded", "0", format_currency(0)])

    category_table = Table(
        category_data, colWidths=[78 * mm, 32 * mm, 40 * mm], repeatRows=1
    )
    category_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#183153")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8D1DC")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F7F9FB")],
                ),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(category_table)
    story.append(Spacer(1, 8 * mm))
    story.append(
        Paragraph(
            "Note: Paid sales represent successful payment amounts. "
            "They are not profit, because product costs and operating expenses "
            "are not currently recorded in the system.",
            normal_style,
        )
    )

    # ---------------------------------------------------------
    # Build the PDF
    # ---------------------------------------------------------
    document.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes


def build_monthly_report_html(report_data: dict) -> str:
    summary = report_data.get("executive_summary", {})
    fulfillment = report_data.get("fulfillment_summary", {})

    return render_template(
        "reports/monthly_admin_report.html",
        # Report metadata
        report_period=format_report_period(
            report_data["report_period"]["start"],
            report_data["report_period"]["end"],
        ),
        # Executive summary
        paid_sales=format_currency(summary.get("paid_sales")),
        total_orders_created=summary.get("total_orders_created", 0),
        unique_buying_customers=summary.get("unique_buying_customers", 0),
        successful_payments=summary.get("successful_payments", 0),
        # Order status
        order_status_summary=report_data.get("order_status_summary", {}),
        # Fulfillment
        orders_shipped_during_month=fulfillment.get("orders_shipped_during_month", 0),
        orders_delivered_during_month=fulfillment.get(
            "orders_delivered_during_month", 0
        ),
        # Product and category performance
        top_products=[
            {**item, "revenue": format_currency(item.get("revenue"))}
            for item in report_data.get("top_products", [])
        ],
        category_performance=[
            {**item, "revenue": format_currency(item.get("revenue"))}
            for item in report_data.get("category_performance", [])
        ],
    )


def build_monthly_report_message(report_data: dict) -> str:
    period = report_data["report_period"]
    summary = report_data["executive_summary"]
    fulfillment = report_data["fulfillment_summary"]

    order_status = report_data.get("order_status_summary", {})
    top_products = report_data.get("top_products", [])
    categories = report_data.get("category_performance", [])

    lines = [
        "📊 *E-Commerce Monthly Admin Report*",
        f"*Reporting period:* {format_report_period(period['start'], period['end'])}",
        "",
        "*Executive Summary*",
        f"• Paid sales: *{format_currency(summary.get('paid_sales'))}*",
        f"• Orders created: *{summary.get('total_orders_created', 0):,}*",
        f"• Unique buying customers: *{summary.get('unique_buying_customers', 0):,}*",
        f"• Successful payments: *{summary.get('successful_payments', 0):,}*",
        "",
        "*Fulfillment*",
        f"• Orders shipped: {fulfillment.get('orders_shipped_during_month', 0):,}",
        f"• Orders delivered: {fulfillment.get('orders_delivered_during_month', 0):,}",
        "",
        "*Order Status*",
    ]

    if order_status:
        for status, count in order_status.items():
            lines.append(f"• {status.replace('_', ' ').title()}: {count:,}")
    else:
        lines.append("• No orders recorded.")

    lines.extend(["", "*Top Products*"])

    if top_products:
        for product in top_products[:5]:
            lines.append(
                f"• {product['product_name']} — "
                f"{product['quantity_sold']:,} sold, "
                f"{format_currency(product.get('revenue'))}"
            )
    else:
        lines.append("• No product sales recorded.")

    lines.extend(["", "*Top Categories*"])

    if categories:
        for category in categories[:5]:
            lines.append(
                f"• {category['category']} — "
                f"{category['quantity_sold']:,} sold, "
                f"{format_currency(category.get('revenue'))}"
            )
    else:
        lines.append("• No category sales recorded.")

    lines.extend(
        [
            "",
            "_Note: Paid sales represent successful payment amounts, not profit._",
            "",
            "The detailed PDF report is available on the backend server.",
        ]
    )

    return "\n".join(lines)
