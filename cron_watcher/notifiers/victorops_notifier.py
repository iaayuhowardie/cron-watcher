import logging
import requests
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class VictorOpsConfig:
    routing_key: str
    rest_endpoint_url: str
    entity_display_name: Optional[str] = "cron-watcher"
    timeout: int = 10


class VictorOpsNotifier:
    def __init__(self, config: VictorOpsConfig) -> None:
        self.config = config

    def send(self, subject: str, body: str) -> bool:
        url = f"{self.config.rest_endpoint_url.rstrip('/')}/{self.config.routing_key}"
        payload = {
            "message_type": "CRITICAL",
            "entity_display_name": self.config.entity_display_name,
            "state_message": body,
            "monitoring_tool": "cron-watcher",
        }
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            logger.debug("VictorOps alert sent: %s", subject)
            return True
        except requests.RequestException as exc:
            logger.error("VictorOps notification failed: %s", exc)
            return False
