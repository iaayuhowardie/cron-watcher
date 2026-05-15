"""Email notifier for cron-watcher alerts."""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    smtp_host: str
    smtp_port: int
    sender: str
    recipients: list[str]
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = True


class EmailNotifier:
    def __init__(self, config: EmailConfig) -> None:
        self.config = config

    def send(self, subject: str, body: str) -> bool:
        """Send an email notification. Returns True on success."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.config.sender
        msg["To"] = ", ".join(self.config.recipients)
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                if self.config.username and self.config.password:
                    server.login(self.config.username, self.config.password)
                server.sendmail(
                    self.config.sender,
                    self.config.recipients,
                    msg.as_string(),
                )
            logger.info("Email alert sent to %s", self.config.recipients)
            return True
        except smtplib.SMTPException as exc:
            logger.error("Failed to send email alert: %s", exc)
            return False
