import logging
import requests
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class RocketChatConfig:
    url: str
    username: str
    password: str
    channel: str
    alias: Optional[str] = "Cron Watcher"
    emoji: Optional[str] = ":alarm_clock:"


class RocketChatNotifier:
    def __init__(self, config: RocketChatConfig) -> None:
        self.config = config
        self._token: Optional[str] = None
        self._user_id: Optional[str] = None

    def _authenticate(self) -> bool:
        try:
            resp = requests.post(
                f"{self.config.url}/api/v1/login",
                json={"username": self.config.username, "password": self.config.password},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})
            self._token = data.get("authToken")
            self._user_id = data.get("userId")
            return bool(self._token and self._user_id)
        except requests.RequestException as exc:
            logger.error("RocketChat authentication failed: %s", exc)
            return False

    def send(self, subject: str, message: str) -> bool:
        if not self._authenticate():
            return False
        payload = {
            "channel": self.config.channel,
            "text": f"*{subject}*\n{message}",
            "alias": self.config.alias,
            "emoji": self.config.emoji,
        }
        try:
            resp = requests.post(
                f"{self.config.url}/api/v1/chat.postMessage",
                json=payload,
                headers={
                    "X-Auth-Token": self._token,
                    "X-User-Id": self._user_id,
                },
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json().get("success", False)
        except requests.RequestException as exc:
            logger.error("RocketChat send failed: %s", exc)
            return False
