from dataclasses import dataclass, field
from typing import Optional
import logging

try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger(__name__)


@dataclass
class CampfireConfig:
    account: str
    token: str
    room_id: str
    timeout: int = 10
    ssl: bool = True


class CampfireNotifier:
    def __init__(self, config: CampfireConfig) -> None:
        self.config = config

    def send(self, subject: str, body: str) -> bool:
        if requests is None:
            logger.error("requests library is not installed")
            return False

        scheme = "https" if self.config.ssl else "http"
        url = (
            f"{scheme}://{self.config.account}.campfirenow.com"
            f"/room/{self.config.room_id}/speak.json"
        )
        payload = {"message": {"type": "TextMessage", "body": f"{subject}\n{body}"}}
        try:
            response = requests.post(
                url,
                json=payload,
                auth=(self.config.token, "x"),
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            logger.debug("Campfire notification sent to room %s", self.config.room_id)
            return True
        except requests.RequestException as exc:
            logger.error("Campfire notification failed: %s", exc)
            return False
