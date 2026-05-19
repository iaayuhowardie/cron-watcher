import logging
from dataclasses import dataclass
from typing import Optional

import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

CLICKSEND_API_URL = "https://rest.clicksend.com/v3/sms/send"


@dataclass
class ClickSendConfig:
    username: str
    api_key: str
    from_number: str
    to_number: str
    timeout: int = 10


class ClickSendNotifier:
    def __init__(self, config: ClickSendConfig) -> None:
        self.config = config

    def send(self, subject: str, message: str) -> bool:
        payload = {
            "messages": [
                {
                    "source": "cron-watcher",
                    "from": self.config.from_number,
                    "to": self.config.to_number,
                    "body": f"{subject}: {message}",
                }
            ]
        }
        try:
            response = requests.post(
                CLICKSEND_API_URL,
                json=payload,
                auth=HTTPBasicAuth(self.config.username, self.config.api_key),
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            logger.debug("ClickSend notification sent to %s", self.config.to_number)
            return True
        except requests.RequestException as exc:
            logger.error("ClickSend notification failed: %s", exc)
            return False
