from dataclasses import dataclass
import logging
import urllib.request
import urllib.error
import json

logger = logging.getLogger(__name__)


@dataclass
class FreshstatusConfig:
    api_key: str
    monitor_id: str
    base_url: str = "https://api.freshstatus.io/v1"
    timeout: int = 10


class FreshstatusNotifier:
    def __init__(self, config: FreshstatusConfig) -> None:
        self.config = config

    def send(self, subject: str, body: str) -> bool:
        url = f"{self.config.base_url}/incidents/"
        payload = json.dumps({
            "title": subject,
            "description": body,
            "monitor_ids": [self.config.monitor_id],
            "incident_type": 1,
            "status": 1,
        }).encode()
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Basic {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout):
                logger.debug(
                    "Freshstatus incident created for monitor %s",
                    self.config.monitor_id,
                )
                return True
        except urllib.error.URLError as exc:
            logger.error("Freshstatus notification failed: %s", exc)
            return False
