import logging
import smtplib
from email.message import EmailMessage
from typing import Optional

from app.core.config import settings


logger = logging.getLogger(__name__)


def _smtp_configured() -> bool:
    return (
        settings.SMTP_HOST is not None
        and settings.SMTP_PORT is not None
        and settings.SMTP_FROM_EMAIL is not None
    )


def _send_via_smtp(to_email: str, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)


def send_otp_email(email: str, otp_code: str) -> None:
    """
    Dev-friendly OTP sender.

    - In development: logs OTP to console so you can copy it.
    - If SMTP settings are provided in .env: sends a real email.
    """
    subject = "Your Todo App OTP Code"
    body = f"Your OTP code is: {otp_code}\n\nThis code will expire shortly."

    if _smtp_configured():
        try:
            _send_via_smtp(email, subject, body)
            logger.info("Sent OTP email via SMTP to %s", email)
        except Exception as exc:  # pragma: no cover - best-effort
            logger.error("Failed to send OTP email via SMTP: %s", exc)
    else:
        # Development fallback: just log the OTP
        logger.warning("SMTP not configured. Printing OTP to console for %s", email)
        print(f"[DEV OTP] Email: {email}, OTP: {otp_code}")

