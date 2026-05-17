import pytest
from unittest.mock import patch, MagicMock
from cron_watcher.notifiers import get_notifier
from cron_watcher.notifiers.googlechat_notifier import GoogleChatNotifier


def _mock_response(status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.raise_for_status.return_value = None
    return mock


def test_get_notifier_returns_googlechat_notifier() -> None:
    config = {
        "type": "googlechat",
        "webhook_url": "https://chat.googleapis.com/v1/spaces/XXX/messages",
    }
    notifier = get_notifier(config)
    assert isinstance(notifier, GoogleChatNotifier)


def test_get_notifier_googlechat_case_insensitive() -> None:
    config = {
        "type": "GoogleChat",
        "webhook_url": "https://chat.googleapis.com/v1/spaces/XXX/messages",
    }
    notifier = get_notifier(config)
    assert isinstance(notifier, GoogleChatNotifier)


def test_get_notifier_googlechat_send_returns_true() -> None:
    config = {
        "type": "googlechat",
        "webhook_url": "https://chat.googleapis.com/v1/spaces/XXX/messages",
    }
    notifier = get_notifier(config)
    with patch("requests.post", return_value=_mock_response(200)):
        assert notifier.send("Subject", "Body") is True


def test_get_notifier_googlechat_with_thread_key() -> None:
    config = {
        "type": "googlechat",
        "webhook_url": "https://chat.googleapis.com/v1/spaces/XXX/messages",
        "thread_key": "cron-alerts",
    }
    notifier = get_notifier(config)
    assert isinstance(notifier, GoogleChatNotifier)
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Subject", "Body")
        _, kwargs = mock_post.call_args
        assert kwargs["params"]["threadKey"] == "cron-alerts"
