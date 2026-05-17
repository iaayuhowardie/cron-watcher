from dataclasses import dataclass, field
from typing import Optional
import requests


@dataclass
class BearyChat Config:
    webhook_url: str
    channel: Optional[str] = None
    timeout: int = 10


class BearyChatNotifier:
    def __init__(self, config: BearyChatConfig) -> None:
        self._config = config

    def send(self, subject: str, body: str) -> bool:
        payload: dict = {
            "text": f"**{subject}**\n{body}",
            "markdown": True,
        }
        if self._config.channel:
            payload["channel"] = self._config.channel

        try:
            resp = requests.post(
                self._config.webhook_url,
                json=payload,
                timeout=self._config.timeout,
            )
            resp.raise_for_status()
            return True
        except requests.RequestException:
            return False
