from unittest.mock import patch, MagicMock
import pytest
from cron_watcher.notifiers import get_notifier


def _mock_response():
    resp = MagicMock()
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def test_get_notifier_returns_grafana_notifier():
    cfg = {
        "url": "https://grafana.example.com",
        "api_key": "glsa_key",
    }
    notifier = get_notifier("grafana", cfg)
    assert notifier is not None
    from cron_watcher.notifiers.grafana_notifier import GrafanaNotifier
    assert isinstance(notifier, GrafanaNotifier)


def test_get_notifier_grafana_case_insensitive():
    cfg = {
        "url": "https://grafana.example.com",
        "api_key": "key",
    }
    assert get_notifier("Grafana", cfg) is not None
    assert get_notifier("GRAFANA", cfg) is not None


def test_get_notifier_grafana_send_returns_true():
    cfg = {
        "url": "https://grafana.example.com",
        "api_key": "glsa_key",
        "tags": ["cron"],
    }
    notifier = get_notifier("grafana", cfg)
    with patch("urllib.request.urlopen", return_value=_mock_response()):
        assert notifier.send("Test subject", "Test message") is True


def test_get_notifier_grafana_with_custom_tags():
    cfg = {
        "url": "https://grafana.example.com",
        "api_key": "key",
        "tags": ["production", "cron", "critical"],
    }
    notifier = get_notifier("grafana", cfg)
    from cron_watcher.notifiers.grafana_notifier import GrafanaNotifier
    assert isinstance(notifier, GrafanaNotifier)
    assert notifier.config.tags == ["production", "cron", "critical"]


def test_get_notifier_grafana_with_custom_timeout():
    cfg = {
        "url": "https://grafana.example.com",
        "api_key": "key",
        "timeout": 30,
    }
    notifier = get_notifier("grafana", cfg)
    assert notifier.config.timeout == 30
