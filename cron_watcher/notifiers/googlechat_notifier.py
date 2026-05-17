from dataclasses import dataclass
from typing import Optional
import requests


@dataclass
class GoogleChatConfig:
    webhook_url: str
    timeout: int = 10
    thread_key: Optional[str] = None


class GoogleChatNotifier:
    def __init__(self, config: GoogleChatConfig) -> None:
        self._config = config

    def send(self, subject: str, body: str) -> bool:
        payload: dict = {
            "text": f"*{subject}*\n{body}"
        }

        params: dict = {}
        if self._config.thread_key:
            params["threadKey"] = self._config.thread_key

        try:
            response = requests.post(
                self._config.webhook_url,
                json=payload,
                params=params if params else None,
                timeout=self._config.timeout,
            )
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False
