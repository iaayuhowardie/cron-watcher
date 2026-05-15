"""Log-based notifier that writes alerts to a file or stdout."""

import logging
import sys
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LogConfig:
    """Configuration for the log notifier."""

    log_file: Optional[str] = None  # None means stdout
    log_level: str = "WARNING"
    log_format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


class LogNotifier:
    """Notifier that logs alerts using Python's logging module."""

    def __init__(self, config: LogConfig) -> None:
        self.config = config
        self._logger = logging.getLogger("cron_watcher.alerts")
        self._logger.setLevel(getattr(logging, config.log_level.upper(), logging.WARNING))

        if not self._logger.handlers:
            formatter = logging.Formatter(config.log_format)

            if config.log_file:
                handler: logging.Handler = logging.FileHandler(config.log_file)
            else:
                handler = logging.StreamHandler(sys.stdout)

            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def send(self, subject: str, message: str) -> bool:
        """Log the alert message.

        Args:
            subject: Alert subject used as a prefix in the log entry.
            message: Alert body.

        Returns:
            True always — logging does not fail silently in a way we need
            to surface to callers.
        """
        try:
            self._logger.warning("[%s] %s", subject, message)
            return True
        except Exception as exc:  # pragma: no cover
            sys.stderr.write(f"LogNotifier error: {exc}\n")
            return False
