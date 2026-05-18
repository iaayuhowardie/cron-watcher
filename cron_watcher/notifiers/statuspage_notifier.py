from dataclasses import dataclass, field
from typing import Optional
import logging
import urllib.request
import urllib.error
import json

logger = logging.getLogger(__name__)


@dataclass
class StatuspageConfig:
    api_key: str
    page_id: str
    component_id: str
    incident_name: str = "Cron Job Alert"
    timeout: int = 10
    base_url: str = "https://api.statuspage.io/v1"


class StatuspageNotifier:
    def __init__(self, config: StatuspageConfig) -> None:
        self.config = config

    def send(self, subject: str, body: str) -> bool:
        url = (
            f"{self.config.base_url}/pages/{self.config.page_id}/incidents"
        )
        payload = json.dumps({
            "incident": {
                "name": self.config.incident_name,
                "status": "investigating",
                "body": f"{subject}\n\n{body}",
                "components": {
                    self.config.component_id: "degraded_performance"
                },
                "component_ids": [self.config.component_id],
            }
        }).encode()
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"OAuth {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout):
                logger.debug("Statuspage incident created for page %s", self.config.page_id)
                return True
        except urllib.error.URLError as exc:
            logger.error("Statuspage notification failed: %s", exc)
            return False
