import pytest
import requests
from unittest.mock import MagicMock, patch
from cron_watcher.notifiers.bearychat_notifier import BearyChatConfig, BearyChatNotifier


@pytest.fixture
def bearychat_config():
    return BearyChatConfig(
        webhook_url="https://hook.bearychat.com/incomingwebhook/abc123",
        channel="#alerts",
    )


@pytest.fixture
def notifier(bearychat_config):
    return BearyChatNotifier(bearychat_config)


def _mock_response(status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError()
    else:
        mock.raise_for_status.return_value = None
    return mock


def test_send_returns_true_on_success(notifier):
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        result = notifier.send("Job missed", "backup_job did not run")
    assert result is True
    mock_post.assert_called_once()


def test_send_posts_correct_payload(notifier):
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Alert", "Details here")
    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert "**Alert**" in payload["text"]
    assert "Details here" in payload["text"]
    assert payload["markdown"] is True
    assert payload["channel"] == "#alerts"


def test_send_includes_channel_when_set(bearychat_config):
    bearychat_config.channel = "#ops"
    notifier = BearyChatNotifier(bearychat_config)
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("x", "y")
    payload = mock_post.call_args[1]["json"]
    assert payload["channel"] == "#ops"


def test_send_omits_channel_when_none():
    config = BearyChatConfig(webhook_url="https://hook.bearychat.com/abc")
    notifier = BearyChatNotifier(config)
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("x", "y")
    payload = mock_post.call_args[1]["json"]
    assert "channel" not in payload


def test_send_returns_false_on_request_error(notifier):
    with patch("requests.post", side_effect=requests.RequestException("timeout")):
        result = notifier.send("Alert", "body")
    assert result is False


def test_send_returns_false_on_http_error(notifier):
    with patch("requests.post", return_value=_mock_response(500)):
        result = notifier.send("Alert", "body")
    assert result is False
