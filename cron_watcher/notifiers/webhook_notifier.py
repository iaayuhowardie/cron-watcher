from dataclasses import dataclass
from typing import Optional
import json
import urllib.request
import urllib.error


@dataclass
class WebhookConfig:
    url: str
    secret: Optional[str] = None
    timeout: int = 10


class WebhookNotifier:
    def __init__(self, config: WebhookConfig) -> None:
        self.config = config

    def send(self, subject: str, body: str) -> bool:
        payload = json.dumps({"subject": subject, "body": body}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.config.secret:
            headers["X-Webhook-Secret"] = self.config.secret

        req = urllib.request.Request(
            self.config.url,
            data=payload,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
                return resp.status < 400
        except (urllib.error.URLError, urllib.error.HTTPError, OSError):
            return False
