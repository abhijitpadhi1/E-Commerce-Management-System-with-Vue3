import logging

import requests
from flask import current_app


logger = logging.getLogger(__name__)


def send_google_chat_message(message: str) -> bool:
    """
    Send a plain-text message to the configured Google Chat space.

    Returns:
        True if Google Chat accepts the message.
        False if the webhook is not configured or the request fails.
    """

    webhook_url = current_app.config.get("GOOGLE_CHAT_WEBHOOK_URL")

    if not webhook_url:
        logger.error("Google Chat webhook URL is not configured.")
        return False

    payload = {"text": message}

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Google Chat notification sent successfully.")
        return True
    except requests.exceptions.RequestException:
        logger.exception("Failed to send Google Chat notification.")
        return False
