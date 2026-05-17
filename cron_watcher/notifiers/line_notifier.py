from dataclasses import dataclass, field
from typing import Optional
import urllib.request
import urllib.parse
import urllib.error


@dataclass
class LineConfig:
    channel_access_token: str
    to: str  # User ID or Group ID
    timeout: int = field(default=10)


class LineNotifier:
    API_URL = "https://api.line.me/v2/bot/message/push"

    def __init__(self, config: LineConfig) -> None:
        self.config = config

    def send(self, subject: str, message: str) -> bool:
        payload = {
            "to": self.config.to,
            "messages": [
                {
                    "type": "text",
                    "text": f"{subject}\n{message}",
                }
            ],
        }
        import json
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.API_URL,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.channel_access_token}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout):
                return True
        except urllib.error.URLError:
            return False
