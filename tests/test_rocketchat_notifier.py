import pytest
from unittest.mock import patch, MagicMock
from cron_watcher.notifiers.rocketchat_notifier import RocketChatConfig, RocketChatNotifier


@pytest.fixture
def rocketchat_config():
    return RocketChatConfig(
        url="https://chat.example.com",
        username="bot",
        password="secret",
        channel="#alerts",
    )


@pytest.fixture
def notifier(rocketchat_config):
    return RocketChatNotifier(rocketchat_config)


def _mock_auth_response():
    mock = MagicMock()
    mock.raise_for_status.return_value = None
    mock.json.return_value = {
        "data": {"authToken": "tok123", "userId": "uid456"}
    }
    return mock


def _mock_post_response(success=True):
    mock = MagicMock()
    mock.raise_for_status.return_value = None
    mock.json.return_value = {"success": success}
    return mock


def test_send_returns_true_on_success(notifier):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = [_mock_auth_response(), _mock_post_response(True)]
        result = notifier.send("Job failed", "backup_job missed its schedule")
    assert result is True


def test_send_posts_correct_payload(notifier):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = [_mock_auth_response(), _mock_post_response(True)]
        notifier.send("Alert", "Something went wrong")
        _, kwargs = mock_post.call_args
        payload = kwargs["json"]
    assert payload["channel"] == "#alerts"
    assert "Alert" in payload["text"]
    assert payload["alias"] == "Cron Watcher"
    assert payload["emoji"] == ":alarm_clock:"


def test_send_returns_false_on_auth_failure(notifier):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception("connection refused")
        result = notifier.send("Alert", "msg")
    assert result is False


def test_send_returns_false_on_post_error(notifier):
    import requests
    with patch("requests.post") as mock_post:
        mock_post.side_effect = [_mock_auth_response(), requests.RequestException("timeout")]
        result = notifier.send("Alert", "msg")
    assert result is False


def test_send_uses_auth_headers(notifier):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = [_mock_auth_response(), _mock_post_response(True)]
        notifier.send("Subject", "Body")
        post_call = mock_post.call_args_list[1]
        headers = post_call[1]["headers"]
    assert headers["X-Auth-Token"] == "tok123"
    assert headers["X-User-Id"] == "uid456"


def test_send_returns_false_when_success_false(notifier):
    with patch("requests.post") as mock_post:
        mock_post.side_effect = [_mock_auth_response(), _mock_post_response(False)]
        result = notifier.send("Alert", "msg")
    assert result is False
