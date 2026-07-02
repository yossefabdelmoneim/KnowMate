import logging
import smtplib
from email.mime.text import MIMEText

from app.Back_End.core.config import settings

logger = logging.getLogger(__name__)


def send_verification_email(to_email: str, company_name: str, verification_link: str) -> None:
    if not settings.smtp_username or not settings.smtp_from_email:
        logger.warning("SMTP not configured — verification email not sent to %s", to_email)
        return

    subject = f"Verify your company '{company_name}' on KnowMate"
    body = f"""
Hello,

Please verify your email to complete registration for {company_name}.

Click the link below:
{verification_link}

This link expires in 30 minutes.

Best,
KnowMate Team
"""

    msg = MIMEText(body.strip(), "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_use_tls:
                server.starttls()
            server.login(settings.smtp_username, settings.smtp_password.get_secret_value())
            server.sendmail(settings.smtp_from_email, [to_email], msg.as_string())
        logger.info("Verification email sent to %s", to_email)
    except Exception:
        logger.exception("Failed to send verification email to %s", to_email)
        raise


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    if not settings.smtp_username or not settings.smtp_from_email:
        logger.warning("SMTP not configured — password reset email not sent to %s", to_email)
        return

    subject = "Reset your KnowMate password"
    body = f"""
Hello,

You requested a password reset for your KnowMate account.

Click the link below to reset your password:
{reset_link}

This link expires in 30 minutes.

If you did not request a password reset, please ignore this email.

Best,
KnowMate Team
"""

    msg = MIMEText(body.strip(), "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_use_tls:
                server.starttls()
            server.login(settings.smtp_username, settings.smtp_password.get_secret_value())
            server.sendmail(settings.smtp_from_email, [to_email], msg.as_string())
        logger.info("Password reset email sent to %s", to_email)
    except Exception:
        logger.exception("Failed to send password reset email to %s", to_email)
        raise
