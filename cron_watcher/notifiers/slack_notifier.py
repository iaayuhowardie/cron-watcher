import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class SlackConfig:
    webhook_url: str
    channel: Optional[str] = None
    username: str = "cron-watcher"
    icon_emoji: str = ":warning:"


class SlackNotifier:
    def __init__(self, config: SlackConfig) -> None:
        self.config = config

    def send(self, subject: str, body: str) -> bool:
        payload: dict = {
            "username": self.config.username,
            "icon_emoji": self.config.icon_emoji,
            "attachments": [
                {
                    "color": "danger",
                    "title": subject,
                    "text": body,
                    "fallback": f"{subject}: {body}",
                }
            ],
        }

        if self.config.channel:
            payload["channel"] = self.config.channel

        try:
            response = requests.post(
                self.config.webhook_url,
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            logger.info("Slack notification sent: %s", subject)
            return True
        except requests.RequestException as exc:
            logger.error("Failed to send Slack notification: %s", exc)
            return False
