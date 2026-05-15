"""Microsoft Teams notifier via incoming webhook."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class TeamsConfig:
    """Configuration for Microsoft Teams notifications."""

    webhook_url: str
    timeout: int = 10
    theme_color: str = "FF0000"


class TeamsNotifier:
    """Send alerts to a Microsoft Teams channel via an incoming webhook."""

    def __init__(self, config: TeamsConfig) -> None:
        self._config = config

    def send(self, subject: str, body: str) -> bool:
        """Post an adaptive message card to the configured Teams webhook.

        Args:
            subject: The card title / alert summary.
            body:    The detailed alert message.

        Returns:
            True on success, False otherwise.
        """
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "themeColor": self._config.theme_color,
            "summary": subject,
            "sections": [
                {
                    "activityTitle": subject,
                    "activityText": body,
                }
            ],
        }

        try:
            response = requests.post(
                self._config.webhook_url,
                json=payload,
                timeout=self._config.timeout,
            )
            response.raise_for_status()
            logger.debug("Teams notification sent: %s", subject)
            return True
        except requests.RequestException as exc:
            logger.error("Failed to send Teams notification: %s", exc)
            return False
