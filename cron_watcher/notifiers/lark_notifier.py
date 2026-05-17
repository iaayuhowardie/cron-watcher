from dataclasses import dataclass
from typing import Optional
import requests


@dataclass
class LarkConfig:
    webhook_url: str
    timeout: int = 10
    secret: Optional[str] = None


class LarkNotifier:
    """Notifier for Lark / Feishu incoming webhooks."""

    def __init__(self, config: LarkConfig) -> None:
        self._config = config

    def send(self, subject: str, body: str) -> bool:
        payload = {
            "msg_type": "text",
            "content": {"text": f"{subject}\n{body}"},
        }
        try:
            resp = requests.post(
                self._config.webhook_url,
                json=payload,
                timeout=self._config.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            # Lark returns {"code": 0} on success
            return data.get("code", -1) == 0
        except requests.RequestException:
            return False
