import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class GotifyConfig:
    url: str
    token: str
    priority: int = 5
    timeout: int = 10


class GotifyNotifier:
    """Notifier that sends alerts via a self-hosted Gotify server."""

    def __init__(self, config: GotifyConfig) -> None:
        self.config = config

    def send(self, subject: str, message: str) -> bool:
        """Send a message to the configured Gotify server.

        Returns True on success, False on failure.
        """
        endpoint = self.config.url.rstrip("/") + "/message"
        headers = {"X-Gotify-Key": self.config.token}
        payload = {
            "title": subject,
            "message": message,
            "priority": self.config.priority,
        }
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            logger.debug("Gotify notification sent: %s", subject)
            return True
        except requests.RequestException as exc:
            logger.error("Failed to send Gotify notification: %s", exc)
            return False
