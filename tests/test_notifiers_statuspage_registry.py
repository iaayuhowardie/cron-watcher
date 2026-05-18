import json
from unittest.mock import MagicMock, patch
import pytest
from cron_watcher.notifiers import get_notifier


def _mock_response():
    mock = MagicMock()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


def test_get_notifier_returns_statuspage_notifier():
    config = {
        "type": "statuspage",
        "api_key": "key",
        "page_id": "pid",
        "component_id": "cid",
    }
    notifier = get_notifier(config)
    assert notifier is not None
    from cron_watcher.notifiers.statuspage_notifier import StatuspageNotifier
    assert isinstance(notifier, StatuspageNotifier)


def test_get_notifier_statuspage_case_insensitive():
    config = {
        "type": "StatusPage",
        "api_key": "key",
        "page_id": "pid",
        "component_id": "cid",
    }
    notifier = get_notifier(config)
    assert notifier is not None


def test_get_notifier_statuspage_send_returns_true():
    config = {
        "type": "statuspage",
        "api_key": "key",
        "page_id": "pid",
        "component_id": "cid",
    }
    notifier = get_notifier(config)
    with patch("urllib.request.urlopen", return_value=_mock_response()):
        result = notifier.send("subject", "body")
    assert result is True


def test_get_notifier_statuspage_with_custom_incident_name():
    config = {
        "type": "statuspage",
        "api_key": "key",
        "page_id": "pid",
        "component_id": "cid",
        "incident_name": "Custom Alert",
    }
    notifier = get_notifier(config)
    assert notifier.config.incident_name == "Custom Alert"


def test_get_notifier_statuspage_with_custom_timeout():
    config = {
        "type": "statuspage",
        "api_key": "key",
        "page_id": "pid",
        "component_id": "cid",
        "timeout": 30,
    }
    notifier = get_notifier(config)
    assert notifier.config.timeout == 30
