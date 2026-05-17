import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)

NEWRELIC_EVENTS_URL = "https://insights-collector.newrelic.com/v1/accounts/{account_id}/events"


@dataclass
class NewRelicConfig:
    account_id: str
    insert_key: str
    event_type: str = "CronWatcherAlert"
    timeout: int = 10


class NewRelicNotifier:
    def __init__(self, config: NewRelicConfig) -> None:
        self.config = config

    def send(self, subject: str, body: str) -> bool:
        url = NEWRELIC_EVENTS_URL.format(account_id=self.config.account_id)
        headers = {
            "X-Insert-Key": self.config.insert_key,
            "Content-Type": "application/json",
        }
        payload = {
            "eventType": self.config.event_type,
            "subject": subject,
            "message": body,
        }
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            logger.debug("New Relic event sent: %s", subject)
            return True
        except requests.RequestException as exc:
            logger.error("New Relic notification failed: %s", exc)
            return False
