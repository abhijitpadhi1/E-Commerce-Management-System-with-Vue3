from app.extensions import celery
from app.models import Order
from app.tasks.export_tasks import export_customer_order_history
from app.tasks.monthly_report_tasks import generate_monthly_admin_report
from app.tasks.reminder_tasks import send_daily_customer_reminders


@celery.task
def count_orders() -> int:
    return Order.query.count()


@celery.task
def add_numbers(a: int, b: int) -> int:
    return a + b
