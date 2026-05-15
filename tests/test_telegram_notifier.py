from unittest.mock import MagicMock, patch

import pytest
import requests

from cron_watcher.notifiers.telegram_notifier import TelegramConfig, TelegramNotifier


@pytest.fixture
def telegram_config():
    return TelegramConfig(
        token="test-bot-token",
        chat_id="-100123456789",
    )


@pytest.fixture
def notifier(telegram_config):
    return TelegramNotifier(telegram_config)


def _mock_response(status_code: int = 200):
    resp = MagicMock()
    resp.status_code = status_code
    if status_code >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError(response=resp)
    else:
        resp.raise_for_status.return_value = None
    return resp


@patch("cron_watcher.notifiers.telegram_notifier.requests.post")
def test_send_returns_true_on_success(mock_post, notifier):
    mock_post.return_value = _mock_response(200)
    result = notifier.send("Test Subject", "Test body")
    assert result is True


@patch("cron_watcher.notifiers.telegram_notifier.requests.post")
def test_send_posts_correct_payload(mock_post, notifier, telegram_config):
    mock_post.return_value = _mock_response(200)
    notifier.send("Alert", "Something went wrong")

    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["chat_id"] == telegram_config.chat_id
    assert "Alert" in payload["text"]
    assert "Something went wrong" in payload["text"]
    assert payload["parse_mode"] == "Markdown"


@patch("cron_watcher.notifiers.telegram_notifier.requests.post")
def test_send_returns_false_on_request_error(mock_post, notifier):
    mock_post.side_effect = requests.ConnectionError("unreachable")
    result = notifier.send("Subject", "Body")
    assert result is False


@patch("cron_watcher.notifiers.telegram_notifier.requests.post")
def test_send_returns_false_on_http_error(mock_post, notifier):
    mock_post.return_value = _mock_response(403)
    result = notifier.send("Subject", "Body")
    assert result is False


@patch("cron_watcher.notifiers.telegram_notifier.requests.post")
def test_send_uses_configured_timeout(mock_post, notifier, telegram_config):
    mock_post.return_value = _mock_response(200)
    notifier.send("Subject", "Body")
    _, kwargs = mock_post.call_args
    assert kwargs["timeout"] == telegram_config.timeout


def test_notifier_url_contains_token(telegram_config):
    n = TelegramNotifier(telegram_config)
    assert telegram_config.token in n._url
