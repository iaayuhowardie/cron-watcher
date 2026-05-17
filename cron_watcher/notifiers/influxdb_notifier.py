from dataclasses import dataclass, field
from typing import Optional
import urllib.request
import urllib.error
import urllib.parse
import json
import time


@dataclass
class InfluxDBConfig:
    url: str
    token: str
    org: str
    bucket: str
    measurement: str = "cron_watcher"
    timeout: int = 10
    tags: dict = field(default_factory=dict)


class InfluxDBNotifier:
    def __init__(self, config: InfluxDBConfig) -> None:
        self._config = config

    def send(self, subject: str, message: str) -> bool:
        cfg = self._config
        timestamp_ns = int(time.time() * 1e9)

        tag_set = ",".join(
            f"{k}={v}" for k, v in cfg.tags.items()
        )
        measurement = cfg.measurement
        if tag_set:
            measurement = f"{measurement},{tag_set}"

        safe_subject = subject.replace(" ", "\ ").replace(",", "\,")
        safe_message = message.replace("\\", "\\\\").replace('"', '\\"')

        line = (
            f'{measurement} subject="{safe_subject}",'
            f'message="{safe_message}" {timestamp_ns}'
        )

        write_url = (
            f"{cfg.url.rstrip('/')}/api/v2/write"
            f"?org={urllib.parse.quote(cfg.org)}"
            f"&bucket={urllib.parse.quote(cfg.bucket)}"
            f"&precision=ns"
        )

        req = urllib.request.Request(
            write_url,
            data=line.encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Token {cfg.token}",
                "Content-Type": "text/plain; charset=utf-8",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=cfg.timeout) as resp:
                return resp.status in (200, 204)
        except (urllib.error.URLError, OSError):
            return False
