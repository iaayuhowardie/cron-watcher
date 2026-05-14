"""Tests for the configuration loader."""

import os
import pytest
import tempfile
import yaml

from cron_watcher.config import load_config, AppConfig, JobConfig, AlertConfig


SAMPLE_CONFIG = {
    "check_interval_seconds": 120,
    "state_file": "/tmp/cron-watcher-state.json",
    "log_level": "DEBUG",
    "alerts": {
        "email": "ops@example.com",
        "webhook_url": "https://hooks.example.com/alert",
    },
    "jobs": [
        {
            "name": "daily-backup",
            "schedule": "0 2 * * *",
            "max_delay_seconds": 600,
            "alert_on_failure": True,
            "alert_on_missed": True,
            "tags": ["backup", "critical"],
        },
        {
            "name": "hourly-cleanup",
            "schedule": "0 * * * *",
        },
    ],
}


@pytest.fixture
def config_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(SAMPLE_CONFIG, f)
        path = f.name
    yield path
    os.unlink(path)


def test_load_config_returns_app_config(config_file):
    config = load_config(config_file)
    assert isinstance(config, AppConfig)


def test_load_config_jobs(config_file):
    config = load_config(config_file)
    assert len(config.jobs) == 2
    assert isinstance(config.jobs[0], JobConfig)
    assert config.jobs[0].name == "daily-backup"
    assert config.jobs[0].schedule == "0 2 * * *"
    assert config.jobs[0].max_delay_seconds == 600
    assert config.jobs[0].tags == ["backup", "critical"]


def test_load_config_job_defaults(config_file):
    config = load_config(config_file)
    cleanup_job = config.jobs[1]
    assert cleanup_job.name == "hourly-cleanup"
    assert cleanup_job.max_delay_seconds == 300
    assert cleanup_job.alert_on_failure is True
    assert cleanup_job.alert_on_missed is True
    assert cleanup_job.tags == []


def test_load_config_alerts(config_file):
    config = load_config(config_file)
    assert isinstance(config.alerts, AlertConfig)
    assert config.alerts.email == "ops@example.com"
    assert config.alerts.webhook_url == "https://hooks.example.com/alert"
    assert config.alerts.slack_channel is None


def test_load_config_top_level_fields(config_file):
    config = load_config(config_file)
    assert config.check_interval_seconds == 120
    assert config.state_file == "/tmp/cron-watcher-state.json"
    assert config.log_level == "DEBUG"


def test_load_config_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.yaml")


def test_load_config_invalid_yaml():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("- just\n- a\n- list\n")
        path = f.name
    try:
        with pytest.raises(ValueError, match="YAML mapping"):
            load_config(path)
    finally:
        os.unlink(path)
