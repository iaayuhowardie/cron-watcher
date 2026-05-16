import pytest
from unittest.mock import patch, MagicMock
from cron_watcher.notifiers import get_notifier


def test_get_notifier_returns_zulip_notifier():
    config = {
        "type": "zulip",
        "site": "https://myorg.zulipchat.com",
        "email": "bot@myorg.zulipchat.com",
        "api_key": "supersecretkey",
        "stream": "alerts",
    }
    notifier = get_notifier(config)
    from cron_watcher.notifiers.zulip_notifier import ZulipNotifier
    assert isinstance(notifier, ZulipNotifier)


def test_get_notifier_zulip_case_insensitive():
    config = {
        "type": "Zulip",
        "site": "https://myorg.zulipchat.com",
        "email": "bot@myorg.zulipchat.com",
        "api_key": "supersecretkey",
        "stream": "alerts",
    }
    notifier = get_notifier(config)
    from cron_watcher.notifiers.zulip_notifier import ZulipNotifier
    assert isinstance(notifier, ZulipNotifier)


def test_get_notifier_zulip_send_returns_true():
    config = {
        "type": "zulip",
        "site": "https://myorg.zulipchat.com",
        "email": "bot@myorg.zulipchat.com",
        "api_key": "supersecretkey",
        "stream": "alerts",
    }
    notifier = get_notifier(config)
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    with patch("requests.post", return_value=mock_resp):
        result = notifier.send("Test", "Message")
    assert result is True


def test_get_notifier_zulip_with_custom_topic():
    config = {
        "type": "zulip",
        "site": "https://myorg.zulipchat.com",
        "email": "bot@myorg.zulipchat.com",
        "api_key": "supersecretkey",
        "stream": "ops",
        "topic": "custom-topic",
    }
    notifier = get_notifier(config)
    assert notifier.config.stream == "ops"
    assert notifier.config.topic == "custom-topic"
