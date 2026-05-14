"""Configuration loader for cron-watcher daemon."""

import os
import yaml
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class JobConfig:
    name: str
    schedule: str
    max_delay_seconds: int = 300
    alert_on_failure: bool = True
    alert_on_missed: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass
class AlertConfig:
    email: Optional[str] = None
    webhook_url: Optional[str] = None
    slack_channel: Optional[str] = None


@dataclass
class AppConfig:
    jobs: List[JobConfig]
    alerts: AlertConfig
    check_interval_seconds: int = 60
    state_file: str = "/var/lib/cron-watcher/state.json"
    log_level: str = "INFO"


def load_config(path: str) -> AppConfig:
    """Load and parse configuration from a YAML file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError("Config file must contain a YAML mapping.")

    jobs = [
        JobConfig(
            name=j["name"],
            schedule=j["schedule"],
            max_delay_seconds=j.get("max_delay_seconds", 300),
            alert_on_failure=j.get("alert_on_failure", True),
            alert_on_missed=j.get("alert_on_missed", True),
            tags=j.get("tags", []),
        )
        for j in raw.get("jobs", [])
    ]

    alert_raw = raw.get("alerts", {})
    alerts = AlertConfig(
        email=alert_raw.get("email"),
        webhook_url=alert_raw.get("webhook_url"),
        slack_channel=alert_raw.get("slack_channel"),
    )

    return AppConfig(
        jobs=jobs,
        alerts=alerts,
        check_interval_seconds=raw.get("check_interval_seconds", 60),
        state_file=raw.get("state_file", "/var/lib/cron-watcher/state.json"),
        log_level=raw.get("log_level", "INFO"),
    )
