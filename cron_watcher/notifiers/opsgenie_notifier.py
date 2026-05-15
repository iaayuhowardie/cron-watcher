import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)

OPSGENIE_ALERT_URL = "https://api.opsgenie.com/v2/alerts"


@dataclass
class OpsGenieConfig:
    api_key: str
    team: Optional[str] = None
    priority: str = "P3"
    tags: Optional[list] = None


class OpsGenieNotifier:
    def __init__(self, config: OpsGenieConfig) -> None:
        self.config = config
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"GenieKey {self.config.api_key}",
                "Content-Type": "application/json",
            }
        )

    def send(self, subject: str, message: str) -> bool:
        payload = {
            "message": subject,
            "description": message,
            "priority": self.config.priority,
        }

        if self.config.team:
            payload["responders"] = [{"name": self.config.team, "type": "team"}]

        if self.config.tags:
            payload["tags"] = self.config.tags

        try:
            response = self._session.post(OPSGENIE_ALERT_URL, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("OpsGenie alert sent: %s", subject)
            return True
        except requests.RequestException as exc:
            logger.error("Failed to send OpsGenie alert: %s", exc)
            return False
