import requests
from dataclasses import dataclass
from typing import Optional


@dataclass
class ZulipConfig:
    site: str
    email: str
    api_key: str
    stream: str
    topic: str = "cron-watcher alerts"


class ZulipNotifier:
    def __init__(self, config: ZulipConfig) -> None:
        self.config = config

    def send(self, subject: str, message: str) -> bool:
        url = f"{self.config.site.rstrip('/')}/api/v1/messages"
        payload = {
            "type": "stream",
            "to": self.config.stream,
            "topic": self.config.topic,
            "content": f"**{subject}**\n\n{message}",
        }
        try:
            response = requests.post(
                url,
                data=payload,
                auth=(self.config.email, self.config.api_key),
                timeout=10,
            )
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False
