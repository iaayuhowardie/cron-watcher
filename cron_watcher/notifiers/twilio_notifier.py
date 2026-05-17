from dataclasses import dataclass
from typing import Optional
import urllib.request
import urllib.parse
import base64
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class TwilioConfig:
    account_sid: str
    auth_token: str
    from_number: str
    to_number: str
    timeout: int = 10


class TwilioNotifier:
    BASE_URL = "https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"

    def __init__(self, config: TwilioConfig) -> None:
        self.config = config

    def send(self, subject: str, message: str) -> bool:
        url = self.BASE_URL.format(sid=self.config.account_sid)
        credentials = f"{self.config.account_sid}:{self.config.auth_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        body = f"{subject}\n\n{message}"
        payload = urllib.parse.urlencode({
            "From": self.config.from_number,
            "To": self.config.to_number,
            "Body": body,
        }).encode()
        try:
            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
                if resp.status in (200, 201):
                    logger.info("Twilio SMS sent to %s", self.config.to_number)
                    return True
                logger.warning("Twilio returned status %d", resp.status)
                return False
        except Exception as exc:
            logger.error("Twilio send failed: %s", exc)
            return False
