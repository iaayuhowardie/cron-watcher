import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class MattermostConfig:
    webhook_url: str
    channel: Optional[str] = None
    username: Optional[str] = "cron-watcher"
    icon_emoji: Optional[str] = ":warning:"
    timeout: int = 10


class MattermostNotifier:
    def __init__(self, config: MattermostConfig) -> None:
        self.config = config

    def send(self, subject: str, body: str) -> bool:
        payload: dict = {
            "text": f"**{subject}**\n{body}",
            "username": self.config.username,
            "icon_emoji": self.config.icon_emoji,
        }
        if self.config.channel:
            payload["channel"] = self.config.channel

        try:
            response = requests.post(
                self.config.webhook_url,
                json=payload,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            return True
        except requests.RequestException as exc:
            logger.error("Mattermost notification failed: %s", exc)
            return False
