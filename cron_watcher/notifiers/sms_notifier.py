"""SMS notifier via Twilio REST API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class SMSConfig:
    account_sid: str
    auth_token: str
    from_number: str
    to_number: str
    timeout: int = 10


class SMSNotifier:
    """Send SMS alerts through the Twilio Messages API."""

    TWILIO_URL = "https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"

    def __init__(self, config: SMSConfig) -> None:
        self.config = config
        self._url = self.TWILIO_URL.format(sid=config.account_sid)

    def send(self, subject: str, body: str) -> bool:
        """Send an SMS message.  Returns True on success, False otherwise."""
        text = f"{subject}\n{body}"
        payload = {
            "From": self.config.from_number,
            "To": self.config.to_number,
            "Body": text[:1600],  # Twilio hard limit
        }
        try:
            response = requests.post(
                self._url,
                data=payload,
                auth=(self.config.account_sid, self.config.auth_token),
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False
