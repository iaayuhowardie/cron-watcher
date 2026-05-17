from dataclasses import dataclass, field
from typing import Optional
import logging
import requests

logger = logging.getLogger(__name__)


@dataclass
class SplunkConfig:
    hec_url: str
    token: str
    index: str = "main"
    source: str = "cron-watcher"
    sourcetype: str = "cron_alert"
    timeout: int = 10
    verify_ssl: bool = True


class SplunkNotifier:
    """Notifier that sends events to Splunk via HTTP Event Collector (HEC)."""

    def __init__(self, config: SplunkConfig) -> None:
        self.config = config
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Splunk {config.token}",
            "Content-Type": "application/json",
        })

    def send(self, subject: str, body: str) -> bool:
        payload = {
            "index": self.config.index,
            "source": self.config.source,
            "sourcetype": self.config.sourcetype,
            "event": {
                "subject": subject,
                "message": body,
            },
        }
        try:
            resp = self._session.post(
                self.config.hec_url,
                json=payload,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
            )
            resp.raise_for_status()
            logger.debug("Splunk HEC event sent: %s", subject)
            return True
        except requests.RequestException as exc:
            logger.error("Splunk HEC send failed: %s", exc)
            return False
