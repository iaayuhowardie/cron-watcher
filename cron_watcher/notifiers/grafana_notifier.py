from dataclasses import dataclass, field
from typing import List
import urllib.request
import urllib.error
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class GrafanaConfig:
    url: str
    api_key: str
    tags: List[str] = field(default_factory=list)
    timeout: int = 10


class GrafanaNotifier:
    """Send annotations to a Grafana instance on cron job events."""

    def __init__(self, config: GrafanaConfig) -> None:
        self.config = config

    def send(self, subject: str, message: str) -> bool:
        payload = {
            "text": f"{subject}\n{message}",
            "tags": self.config.tags,
        }
        data = json.dumps(payload).encode()
        endpoint = self.config.url.rstrip("/") + "/api/annotations"
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout):
                logger.debug("Grafana annotation sent: %s", subject)
                return True
        except urllib.error.URLError as exc:
            logger.error("Grafana notification failed: %s", exc)
            return False
