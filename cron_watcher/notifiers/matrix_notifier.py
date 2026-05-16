import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class MatrixConfig:
    homeserver_url: str
    access_token: str
    room_id: str
    timeout: int = 10


class MatrixNotifier:
    def __init__(self, config: MatrixConfig) -> None:
        self.config = config

    def send(self, subject: str, body: str) -> bool:
        url = (
            f"{self.config.homeserver_url.rstrip('/')}"
            f"/_matrix/client/v3/rooms/{self.config.room_id}/send/m.room.message"
        )
        headers = {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "msgtype": "m.text",
            "body": f"{subject}\n\n{body}",
        }
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            logger.debug(
                "Matrix notification sent to room %s", self.config.room_id
            )
            return True
        except requests.RequestException as exc:
            logger.error("Matrix notification failed: %s", exc)
            return False
