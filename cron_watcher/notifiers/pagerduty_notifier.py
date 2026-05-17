import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)

PAGERDUTY_EVENTS_API = "https://events.pagerduty.com/v2/enqueue"


@dataclass
class PagerDutyConfig:
    integration_key: str
    severity: str = "error"  # critical, error, warning, info
    source: str = "cron-watcher"
    timeout: int = 10


class PagerDutyNotifier:
    def __init__(self, config: PagerDutyConfig) -> None:
        self.config = config

    def send(self, summary: str, details: Optional[dict] = None) -> bool:
        payload = {
            "routing_key": self.config.integration_key,
            "event_action": "trigger",
            "payload": {
                "summary": summary,
                "source": self.config.source,
                "severity": self.config.severity,
                "custom_details": details or {},
            },
        }

        try:
            response = requests.post(
                PAGERDUTY_EVENTS_API,
                json=payload,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            logger.info("PagerDuty alert sent: %s", summary)
            return True
        except requests.exceptions.HTTPError as exc:
            logger.error(
                "PagerDuty HTTP error: %s (status=%s, body=%s)",
                exc,
                exc.response.status_code if exc.response is not None else "unknown",
                exc.response.text if exc.response is not None else "",
            )
            return False
        except requests.exceptions.RequestException as exc:
            logger.error("PagerDuty request failed: %s", exc)
            return False
