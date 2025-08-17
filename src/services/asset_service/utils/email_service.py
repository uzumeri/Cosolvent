import logging
from typing import Optional, Sequence, Union

from src.core.config import settings

logger = logging.getLogger(__name__)


def send_email(subject: str, to_email: Union[str, Sequence[str]], html_body: str) -> None:
    """
    Send an HTML email using Resend.

    Requires env var RESEND_API_KEY to be set.
    Uses From address from SMTP_FROM (default: no-reply@grainplaza.com).
    """
    if not settings.RESEND_API_KEY:
        logger.error("Resend is not configured. Missing RESEND_API_KEY.")
        raise RuntimeError("Resend is not configured")

    try:
        # Import locally to avoid hard import error if not installed at module import time
        import resend  # type: ignore

        resend.api_key = settings.RESEND_API_KEY
        to_list = [to_email] if isinstance(to_email, str) else list(to_email)
        params = {
            "from": "no-reply@grainplaza.com",
            "to": to_list,
            "subject": subject,
            "html": html_body,
        }
        resend.Emails.send(params)  # raises on failure
        logger.info("Sent email via Resend to %s", ",".join(to_list))
    except Exception as e:
        logger.exception("Failed to send email via Resend to %s: %s", to_email, e)
        raise


def send_welcome_email(name: str, to_email: str, temp_password: str, frontend_url: Optional[str] = None) -> None:
    """
    Sends a welcome email with login credentials and sign-in link.
    """
    url = (frontend_url or settings.FRONTEND_URL).rstrip("/") + "/signin"
    subject = "Welcome to GrainPlaza — Your Account Details"
    html = f"""
    <div style='font-family:Arial,sans-serif;line-height:1.6'>
      <h2>Welcome{name and (', ' + name) or ''}!</h2>
      <p>Your producer account is now approved on GrainPlaza.</p>
      <p><strong>Login details</strong></p>
      <ul>
        <li><strong>Email:</strong> {to_email}</li>
        <li><strong>Temporary password:</strong> {temp_password}</li>
      </ul>
      <p>
        Please sign in here: <a href="{url}">{url}</a><br/>
        For security, change your password after signing in.
      </p>
      <p>— GrainPlaza Team</p>
    </div>
    """
    send_email(subject, to_email, html)
