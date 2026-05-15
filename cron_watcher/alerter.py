"""Alert dispatching module for cron-watcher."""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional

from cron_watcher.config import AlertConfig, JobConfig

logger = logging.getLogger(__name__)


class Alerter:
    """Dispatches alerts when cron jobs fail or are missed."""

    def __init__(self, config: AlertConfig) -> None:
        self.config = config

    def send_missed_run_alert(self, job: JobConfig, expected_at: datetime) -> bool:
        """Send an alert for a missed cron job run."""
        subject = f"[cron-watcher] Missed run: {job.name}"
        body = (
            f"Cron job '{job.name}' did not run as expected.\n"
            f"Schedule:   {job.schedule}\n"
            f"Expected at: {expected_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Checked at:  {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
        )
        return self._dispatch(subject, body)

    def send_failure_alert(self, job: JobConfig, exit_code: int, output: Optional[str] = None) -> bool:
        """Send an alert for a cron job that exited with a non-zero status."""
        subject = f"[cron-watcher] Failure: {job.name}"
        body = (
            f"Cron job '{job.name}' failed.\n"
            f"Schedule:  {job.schedule}\n"
            f"Exit code: {exit_code}\n"
        )
        if output:
            body += f"Output:\n{output}\n"
        return self._dispatch(subject, body)

    def _dispatch(self, subject: str, body: str) -> bool:
        """Send an email alert via SMTP."""
        cfg = self.config
        msg = MIMEMultipart()
        msg["From"] = cfg.from_email
        msg["To"] = ", ".join(cfg.to_emails)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port) as server:
                if cfg.smtp_use_tls:
                    server.starttls()
                if cfg.smtp_username and cfg.smtp_password:
                    server.login(cfg.smtp_username, cfg.smtp_password)
                server.sendmail(cfg.from_email, cfg.to_emails, msg.as_string())
            logger.info("Alert sent: %s", subject)
            return True
        except smtplib.SMTPException as exc:
            logger.error("Failed to send alert '%s': %s", subject, exc)
            return False
