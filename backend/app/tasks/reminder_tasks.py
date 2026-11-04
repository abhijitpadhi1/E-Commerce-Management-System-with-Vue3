from celery.utils.log import get_task_logger
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import celery, db
from app.models import User, Cart
from app.services.mail_service import send_email
from app.services.offers import get_best_offer


logger = get_task_logger(__name__)


def build_cart_reminder(
    user: User, cart_items: list[dict], offer_result: dict
) -> tuple[str, str]:
    """Build a personalized reminder for a customer with cart items."""

    item_lines: list[str] = []
    for item in cart_items:
        item_lines.append(
            f"- {item['name']} x {item['quantity']} (₹{item['unit_price'] * item['quantity']:.2f})"
        )

    items_text = "\n".join(item_lines)

    applied_offer = offer_result["applied_offer"]
    if applied_offer:
        offer_text = (
            f"Offer available: {applied_offer['name']} "
            f"({applied_offer['code']})\n"
            f"Estimated discount: ₹{offer_result['discount_amount']:.2f}\n"
        )
    else:
        offer_text = "Check out our current offers and see whether your cart qualifies for a discount.\n"

    subject = "Your shopping cart is waiting for you!"

    body = f"""
Hi {user.name},

You still have items waiting in your shopping cart:

{items_text}

Cart subtotal: ₹{offer_result['subtotal']:.2f}

{offer_text}
Visit our store to review your cart and complete your purchase.

Thank you for shopping with us!
"""

    return subject, body


def build_general_offer_reminder(user: User) -> tuple[str, str]:
    """Build a general promotional reminder for a customer with an empty cart."""

    subject = "Discover today's offers!"

    body = f"""
Hi {user.name},

Your cart is currently empty, but there are great products waiting
for you in our store.

Visit our store to explore the latest products and available offers.

Thank you for shopping with us!
"""

    return subject, body


@celery.task(
    name="app.tasks.reminder_tasks.send_daily_customer_reminders",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_daily_customer_reminders(
    self, dry_run: bool = True, test_recipient: str = None
) -> dict[str, int]:
    """
    Send daily reminders to customers.

    dry_run=True:
        Generate/log reminders without sending emails.

    dry_run=False:
        Send emails to customers.
    """

    customers = User.query.filter_by(role="CUSTOMER").all()

    sent_count = 0
    skipped_count = 0
    failed_count = 0

    logger.info(
        "Starting daily customer reminders. Customers: %s, dry_run: %s",
        len(customers),
        dry_run,
    )

    for user in customers:
        try:
            if not user.email:
                skipped_count += 1
                logger.warning(
                    "Skipping customer ID %s because no email is configured.", user.id
                )
                continue

            cart = Cart.query.filter_by(user_id=user.id).first()
            cart_items = []
            if cart and cart.items:
                for cart_item in cart.items:
                    product = cart_item.product
                    if not product or not product.is_active:
                        continue

                    cart_items.append(
                        {
                            "product_id": product.id,
                            "name": product.name,
                            "category": product.category,
                            "unit_price": product.price,
                            "quantity": cart_item.quantity,
                        }
                    )

            if cart_items:
                subtotal = sum(
                    item["unit_price"] * item["quantity"] for item in cart_items
                )
                offer_result = get_best_offer(cart_items, subtotal)
                subject, body = build_cart_reminder(user, cart_items, offer_result)
            else:
                subject, body = build_general_offer_reminder(user)

            if dry_run:
                logger.info(
                    "DRY RUN — reminder prepared for customer ID %s (%s)",
                    user.id,
                    user.email,
                )
                continue

            recipient = test_recipient or user.email
            send_email(to_email=recipient, subject=subject, body=body)
            sent_count += 1
            logger.info("Reminder sent to customer ID %s (%s)", user.id, recipient)

        except Exception:
            failed_count += 1
            logger.exception("Failed to process reminder for customer ID %s", user.id)
            # Continue to the next customer instead of stopping the batch.
            continue

    result = {
        "total_customers": len(customers),
        "sent": sent_count,
        "skipped": skipped_count,
        "failed": failed_count,
        "dry_run": dry_run,
    }

    logger.info("Daily customer reminders completed: %s", result)

    return result
