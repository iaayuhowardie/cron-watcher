import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)

PUSHBULLET_API_URL = "https://api.pushbullet.com/v2/pushes"


@dataclass
class PushbulletConfig:
    access_token: str
    device_iden: Optional[str] = None
    channel_tag: Optional[str] = None


class PushbulletNotifier:
    def __init__(self, config: PushbulletConfig) -> None:
        self.config = config

    def send(self, subject: str, body: str) -> bool:
        headers = {
            "Access-Token": self.config.access_token,
            "Content-Type": "application/json",
        }
        payload: dict = {
            "type": "note",
            "title": subject,
            "body": body,
        }
        if self.config.device_iden:
            payload["device_iden"] = self.config.device_iden
        if self.config.channel_tag:
            payload["channel_tag"] = self.config.channel_tag

        try:
            response = requests.post(
                PUSHBULLET_API_URL,
                json=payload,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            return True
        except requests.RequestException as exc:
            logger.error("Pushbullet notification failed: %s", exc)
            return False
