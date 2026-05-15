import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)

PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"


@dataclass
class PushoverConfig:
    user_key: str
    api_token: str
    device: Optional[str] = None
    priority: int = 0
    sound: Optional[str] = None


class PushoverNotifier:
    def __init__(self, config: PushoverConfig) -> None:
        self.config = config

    def send(self, subject: str, message: str) -> bool:
        payload = {
            "token": self.config.api_token,
            "user": self.config.user_key,
            "title": subject,
            "message": message,
            "priority": self.config.priority,
        }

        if self.config.device:
            payload["device"] = self.config.device

        if self.config.sound:
            payload["sound"] = self.config.sound

        try:
            response = requests.post(PUSHOVER_API_URL, data=payload, timeout=10)
            response.raise_for_status()
            logger.debug("Pushover notification sent: %s", subject)
            return True
        except requests.RequestException as exc:
            logger.error("Pushover notification failed: %s", exc)
            return False
