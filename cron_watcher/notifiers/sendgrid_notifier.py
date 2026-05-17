from dataclasses import dataclass, field
from typing import List, Optional
import urllib.request
import urllib.error
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class SendGridConfig:
    api_key: str
    from_email: str
    to_emails: List[str]
    subject_prefix: str = "[cron-watcher]"
    timeout: int = 10


class SendGridNotifier:
    API_URL = "https://api.sendgrid.com/v3/mail/send"

    def __init__(self, config: SendGridConfig) -> None:
        self.config = config

    def send(self, subject: str, message: str) -> bool:
        full_subject = f"{self.config.subject_prefix} {subject}".strip()
        payload = {
            "personalizations": [
                {
                    "to": [{"email": addr} for addr in self.config.to_emails],
                    "subject": full_subject,
                }
            ],
            "from": {"email": self.config.from_email},
            "content": [{"type": "text/plain", "value": message}],
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.API_URL,
            data=data,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
                if resp.status in (200, 202):
                    logger.debug("SendGrid notification sent: %s", full_subject)
                    return True
                logger.warning("SendGrid unexpected status: %s", resp.status)
                return False
        except urllib.error.URLError as exc:
            logger.error("SendGrid request failed: %s", exc)
            return False
