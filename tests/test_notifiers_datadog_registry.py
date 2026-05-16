import pytest
from unittest.mock import patch, MagicMock
import requests

from cron_watcher.notifiers import get_notifier


def test_get_notifier_returns_datadog_notifier():
    config = {
        "type": "datadog",
        "api_key": "abc123",
    }
    notifier = get_notifier(config)
    assert notifier is not None
    from cron_watcher.notifiers.datadog_notifier import DatadogNotifier
    assert isinstance(notifier, DatadogNotifier)


def test_get_notifier_datadog_case_insensitive():
    config = {
        "type": "Datadog",
        "api_key": "abc123",
    }
    notifier = get_notifier(config)
    assert notifier is not None


@patch("cron_watcher.notifiers.datadog_notifier.requests.post")
def test_get_notifier_datadog_send_returns_true(mock_post):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp

    config = {
        "type": "datadog",
        "api_key": "abc123",
        "tags": ["env:test"],
    }
    notifier = get_notifier(config)
    result = notifier.send("Test alert", "Something failed")
    assert result is True


def test_get_notifier_datadog_with_all_fields():
    config = {
        "type": "datadog",
        "api_key": "key",
        "app_key": "appkey",
        "host": "worker-01",
        "tags": ["team:ops"],
        "timeout": 15,
    }
    notifier = get_notifier(config)
    assert notifier is not None
    assert notifier.config.host == "worker-01"
    assert notifier.config.timeout == 15
    assert "team:ops" in notifier.config.tags
