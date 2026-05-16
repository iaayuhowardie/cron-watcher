import logging
from dataclasses import dataclass, field
from typing import Optional

import requests

logger = logging.getLogger(__name__)

DATADOG_EVENTS_URL = "https://api.datadoghq.com/api/v1/events"


@dataclass
class DatadogConfig:
    api_key: str
    app_key: Optional[str] = None
    host: Optional[str] = None
    tags: list = field(default_factory=list)
    timeout: int = 10


class DatadogNotifier:
    def __init__(self, config: DatadogConfig) -> None:
        self.config = config

    def send(self, subject: str, body: str) -> bool:
        headers = {
            "Content-Type": "application/json",
            "DD-API-KEY": self.config.api_key,
        }
        if self.config.app_key:
            headers["DD-APPLICATION-KEY"] = self.config.app_key

        tags = list(self.config.tags)
        if self.config.host:
            tags.append(f"host:{self.config.host}")

        payload = {
            "title": subject,
            "text": body,
            "alert_type": "error",
            "tags": tags,
        }

        try:
            response = requests.post(
                DATADOG_EVENTS_URL,
                json=payload,
                headers=headers,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            return True
        except requests.RequestException as exc:
            logger.error("DatadogNotifier failed to send event: %s", exc)
            return False
