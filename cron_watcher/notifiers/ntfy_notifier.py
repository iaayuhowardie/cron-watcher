"""ntfy.sh notifier for cron-watcher."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class NtfyConfig:
    """Configuration for ntfy notifier."""

    topic: str
    server: str = "https://ntfy.sh"
    token: Optional[str] = None
    priority: str = "default"  # min, low, default, high, urgent
    tags: Optional[str] = None  # comma-separated ntfy tags


class NtfyNotifier:
    """Send notifications via ntfy.sh (or self-hosted ntfy server)."""

    def __init__(self, config: NtfyConfig) -> None:
        self.config = config

    def send(self, subject: str, body: str) -> bool:
        """Publish a message to the configured ntfy topic.

        Returns True on success, False on failure.
        """
        url = f"{self.config.server.rstrip('/')}/{self.config.topic}"

        headers: dict[str, str] = {
            "Title": subject,
            "Priority": self.config.priority,
        }

        if self.config.tags:
            headers["Tags"] = self.config.tags

        if self.config.token:
            headers["Authorization"] = f"Bearer {self.config.token}"

        try:
            response = requests.post(
                url,
                data=body.encode("utf-8"),
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False
