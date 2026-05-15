import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/sendMessage"


@dataclass
class TelegramConfig:
    token: str
    chat_id: str
    parse_mode: str = "Markdown"
    timeout: int = 10


class TelegramNotifier:
    def __init__(self, config: TelegramConfig) -> None:
        self.config = config
        self._url = TELEGRAM_API_BASE.format(token=config.token)

    def send(self, subject: str, body: str) -> bool:
        """Send a message via Telegram Bot API.

        Returns True on success, False otherwise.
        """
        payload = {
            "chat_id": self.config.chat_id,
            "text": f"*{subject}*\n\n{body}",
            "parse_mode": self.config.parse_mode,
        }
        try:
            response = requests.post(
                self._url,
                json=payload,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            logger.debug(
                "Telegram notification sent to chat_id=%s", self.config.chat_id
            )
            return True
        except requests.RequestException as exc:
            logger.error("Failed to send Telegram notification: %s", exc)
            return False
