"""Discord webhook notifier for cron-watcher."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class DiscordConfig:
    webhook_url: str
    username: str = "cron-watcher"
    avatar_url: Optional[str] = None
    timeout: int = 10


class DiscordNotifier:
    """Sends alerts to a Discord channel via an incoming webhook."""

    def __init__(self, config: DiscordConfig) -> None:
        self.config = config

    def send(self, subject: str, body: str) -> bool:
        """Post a message to Discord.  Returns True on success."""
        payload: dict = {
            "username": self.config.username,
            "embeds": [
                {
                    "title": subject,
                    "description": body,
                    "color": 0xFF0000,
                }
            ],
        }

        if self.config.avatar_url:
            payload["avatar_url"] = self.config.avatar_url

        try:
            response = requests.post(
                self.config.webhook_url,
                json=payload,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            logger.debug("Discord notification sent: %s", subject)
            return True
        except requests.RequestException as exc:
            logger.error("Discord notification failed: %s", exc)
            return False
