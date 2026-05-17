import logging
from dataclasses import dataclass, field
from typing import Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class MailgunConfig:
    api_key: str
    domain: str
    from_address: str
    to_addresses: list[str]
    subject_prefix: str = "[cron-watcher]"
    api_base_url: str = "https://api.mailgun.net/v3"
    timeout: int = 10


class MailgunNotifier:
    def __init__(self, config: MailgunConfig) -> None:
        self.config = config

    def send(self, subject: str, message: str) -> bool:
        url = f"{self.config.api_base_url}/{self.config.domain}/messages"
        full_subject = f"{self.config.subject_prefix} {subject}"
        payload = {
            "from": self.config.from_address,
            "to": ",".join(self.config.to_addresses),
            "subject": full_subject,
            "text": message,
        }
        try:
            response = requests.post(
                url,
                auth=("api", self.config.api_key),
                data=payload,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            logger.debug(
                "Mailgun notification sent to %s",
                self.config.to_addresses,
            )
            return True
        except requests.RequestException as exc:
            logger.error("Mailgun notification failed: %s", exc)
            return False
