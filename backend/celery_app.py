from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

from celery import signals
from celery.schedules import crontab

from app import create_app
from app.extensions import celery


flask_app = create_app()
celery.flask_app = flask_app


# Celery Beat configuration
celery.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=True,
    beat_schedule={
        "monthly-admin-report": {
            "task": "app.tasks.monthly_report_tasks.generate_monthly_admin_report",
            "schedule": crontab(day_of_month=1, hour=9, minute=0),
        },
        "daily-customer-reminders": {
            "task": "app.tasks.reminder_tasks.send_daily_customer_reminders",
            "schedule": crontab(hour=9, minute=0),
            "kwargs": {
                "dry_run": False,
            },
        },
    },
)


# Log directory and file
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

CELERY_WORKER_LOGFILE = LOG_DIR / "celery_worker.log"
CELERY_BEAT_LOGFILE = LOG_DIR / "celery_beat.log"


@signals.after_setup_logger.connect
def setup_celery_file_logging(logger=None, **kwargs):
    """Write Celery logs to a rotating file while preserving Celery's existing terminal logging."""

    # Prevent duplicate file handlers
    if any(
        getattr(handler, "_celery_file_handler", False) for handler in logger.handlers
    ):
        return

    file_handler = RotatingFileHandler(
        CELERY_WORKER_LOGFILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB per log file
        backupCount=5,  # Keep 5 old log files
        encoding="utf-8",
    )

    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)

    # Mark handler so it isn't added more than once
    file_handler._celery_file_handler = True

    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)


@signals.after_setup_logger.connect
def setup_celery_beat_file_logging(logger=None, **kwargs):
    """Configure a dedicated rotating log file for Celery Beat."""

    if logger is None:
        return

    # Avoid adding duplicate handlers.
    if any(
        getattr(handler, "_celery_beat_file_handler", False)
        for handler in logger.handlers
    ):
        return

    file_handler = RotatingFileHandler(
        CELERY_BEAT_LOGFILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8",
    )

    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)

    # Custom marker prevents duplicate handler registration.
    file_handler._celery_beat_file_handler = True

    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
