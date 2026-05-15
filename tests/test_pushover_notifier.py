from unittest.mock import MagicMock, patch

import pytest
import requests

from cron_watcher.notifiers.pushover_notifier import PushoverConfig, PushoverNotifier


@pytest.fixture
def pushover_config() -> PushoverConfig:
    return PushoverConfig(
        user_key="user_abc123",
        api_token="token_xyz789",
        device="myphone",
        priority=0,
        sound="pushover",
    )


@pytest.fixture
def notifier(pushover_config: PushoverConfig) -> PushoverNotifier:
    return PushoverNotifier(config=pushover_config)


def _mock_response(status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)
    else:
        mock.raise_for_status.return_value = None
    return mock


@patch("cron_watcher.notifiers.pushover_notifier.requests.post")
def test_send_returns_true_on_success(mock_post, notifier):
    mock_post.return_value = _mock_response(200)
    result = notifier.send("Test Subject", "Test message body")
    assert result is True


@patch("cron_watcher.notifiers.pushover_notifier.requests.post")
def test_send_posts_correct_payload(mock_post, notifier, pushover_config):
    mock_post.return_value = _mock_response(200)
    notifier.send("Alert", "Job failed")

    _, kwargs = mock_post.call_args
    payload = kwargs["data"]
    assert payload["user"] == pushover_config.user_key
    assert payload["token"] == pushover_config.api_token
    assert payload["title"] == "Alert"
    assert payload["message"] == "Job failed"
    assert payload["device"] == pushover_config.device
    assert payload["sound"] == pushover_config.sound


@patch("cron_watcher.notifiers.pushover_notifier.requests.post")
def test_send_returns_false_on_http_error(mock_post, notifier):
    mock_post.return_value = _mock_response(400)
    result = notifier.send("Subject", "Message")
    assert result is False


@patch("cron_watcher.notifiers.pushover_notifier.requests.post")
def test_send_returns_false_on_request_exception(mock_post, notifier):
    mock_post.side_effect = requests.ConnectionError("unreachable")
    result = notifier.send("Subject", "Message")
    assert result is False


@patch("cron_watcher.notifiers.pushover_notifier.requests.post")
def test_send_without_optional_fields(mock_post):
    config = PushoverConfig(user_key="u123", api_token="t456")
    plain_notifier = PushoverNotifier(config=config)
    mock_post.return_value = _mock_response(200)

    result = plain_notifier.send("Hello", "World")
    assert result is True

    _, kwargs = mock_post.call_args
    payload = kwargs["data"]
    assert "device" not in payload
    assert "sound" not in payload
