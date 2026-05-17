from dataclasses import dataclass
from typing import Optional
import logging

try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger(__name__)


@dataclass
class SignalWireConfig:
    project_id: str
    api_token: str
    space_url: str
    from_number: str
    to_number: str
    timeout: int = 10


class SignalWireNotifier:
    """Send SMS alerts via SignalWire REST API."""

    def __init__(self, config: SignalWireConfig) -> None:
        self.config = config

    def send(self, subject: str, body: str) -> bool:
        if requests is None:
            logger.error("requests library is required for SignalWireNotifier")
            return False

        url = (
            f"https://{self.config.space_url}/api/laml/2010-04-01"
            f"/Accounts/{self.config.project_id}/Messages.json"
        )
        payload = {
            "From": self.config.from_number,
            "To": self.config.to_number,
            "Body": f"{subject}\n{body}",
        }
        try:
            response = requests.post(
                url,
                data=payload,
                auth=(self.config.project_id, self.config.api_token),
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            logger.debug(
                "SignalWire SMS sent to %s (sid=%s)",
                self.config.to_number,
                response.json().get("sid"),
            )
            return True
        except requests.RequestException as exc:
            logger.error("SignalWire notification failed: %s", exc)
            return False
