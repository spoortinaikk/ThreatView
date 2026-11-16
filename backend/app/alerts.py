
import logging
from urllib.parse import urlparse

from .db import Session
from .models import User
from .config import SENDGRID_API_KEY, MAIL_FROM

log = logging.getLogger("alerts")


def normalize_domain(value):
    """Extract and normalize a domain or URL hostname."""
    if not value:
        return ""

    value = value.strip().lower()

    if not value:
        return ""

    parsed = urlparse(
        value if "://" in value else "//" + value
    )

    hostname = (parsed.hostname or "").lower().rstrip(".")

    if hostname.startswith("www."):
        hostname = hostname[4:]

    return hostname


 
def send_email(to, subject, body):
    """Send an email through SendGrid or log a dry-run message."""

    if not SENDGRID_API_KEY:
        log.info("[email dry-run] to=%s subject=%s", to, subject)
        return

    if not MAIL_FROM:
        raise ValueError("MAIL_FROM is not configured")

    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    message = Mail(
        from_email=MAIL_FROM,
        to_emails=to,
        subject=subject,
        plain_text_content=body
    )

    response = SendGridAPIClient(SENDGRID_API_KEY).send(message)

    log.info(
        "SendGrid response: status=%s recipient=%s",
        response.status_code,
        to
    )

    return response



def rules(user, t):
    """Return an alert reason when a threat matches a user's settings."""

    # Brand/domain monitoring
    if user.domain and t.value:
        configured_domain = normalize_domain(user.domain)

        parsed = urlparse(
            t.value.strip()
            if "://" in t.value
            else "//" + t.value.strip()
        )

        hostname = normalize_domain(parsed.hostname or "")

        if configured_domain and hostname:
            if (
                hostname == configured_domain
                or hostname.endswith("." + configured_domain)
            ):
                return (
                    f"Brand monitoring: {user.domain} "
                    f"appears in {t.source} ({t.ioc_type})"
                )

    # Industry-based alerts
    if user.industry and t.industry:
        user_industry = user.industry.strip().lower()

        threat_industries = [
            item.strip().lower()
            for item in str(t.industry).split(",")
        ]

        if user_industry in threat_industries:
            return (
                f"Industry match ({t.industry}): "
                f"new {t.ioc_type} from {t.source}"
            )

    return None


def dispatch_alerts(threats):
    """Find matching threats and notify registered users."""

    if not threats:
        return

    with Session() as s:
        users = s.query(User).all()

        for user in users:
            hits = [
                (threat, reason)
                for threat in threats
                if (reason := rules(user, threat))
            ]

            if hits:
                body = "\n".join(
                    f"- {reason}: {threat.value}"
                    for threat, reason in hits[:50]
                )

                send_email(
                    user.email,
                    f"ThreatView: {len(hits)} new alert(s)",
                    body
                )
