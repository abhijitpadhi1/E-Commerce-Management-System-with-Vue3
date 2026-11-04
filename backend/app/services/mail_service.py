from pathlib import Path
from flask import current_app
from flask_mail import Message

from app.extensions import mail


def send_email(
    to_email: str, subject: str, body: str, attachment_path: Path | None = None
) -> None:
    message = Message(
        subject=subject,
        recipients=[to_email],
        body=body,
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
    )

    if attachment_path:
        attachment_path = Path(attachment_path)

        with attachment_path.open("rb") as attachment:
            message.attach(
                filename=attachment_path.name,
                content_type=(
                    "text/csv"
                    if attachment_path.suffix == ".csv"
                    else "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                data=attachment.read(),
            )

    mail.send(message)
