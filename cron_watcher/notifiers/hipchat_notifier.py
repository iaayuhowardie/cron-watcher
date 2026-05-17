import logging
from dataclasses import dataclass, field
from typing import Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class HipChatConfig:
    token: str
    room_id: str
    server_url: str = "https://api.hipchat.com"
    color: str = "red"
    notify: bool = True
    timeout: int = 10
    message_format: str = "text"


class HipChatNotifier:
    def __init__(self, config: HipChatConfig) -> None:
        self.config = config

    def send(self, subject: str, body: str) -> bool:
        url = (
            f"{self.config.server_url.rstrip('/')}"
            f"/v2/room/{self.config.room_id}/notification"
        )
        headers = {
            "Authorization": f"Bearer {self.config.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "message": f"**{subject}**\n{body}",
            "color": self.config.color,
            "notify": self.config.notify,
            "message_format": self.config.message_format,
        }
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            logger.debug("HipChat notification sent to room %s", self.config.room_id)
            return True
        except requests.RequestException as exc:
            logger.error("HipChat notification failed: %s", exc)
            return False
