from unittest.mock import MagicMock, patch

import pytest
import requests

from cron_watcher.notifiers.hipchat_notifier import HipChatConfig, HipChatNotifier


@pytest.fixture
def hipchat_config():
    return HipChatConfig(
        token="test-token",
        room_id="123456",
        server_url="https://api.hipchat.com",
        color="red",
        notify=True,
    )


@pytest.fixture
def notifier(hipchat_config):
    return HipChatNotifier(hipchat_config)


def _mock_response(status_code=204):
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)
    else:
        mock.raise_for_status.return_value = None
    return mock


@patch("cron_watcher.notifiers.hipchat_notifier.requests.post")
def test_send_returns_true_on_success(mock_post, notifier):
    mock_post.return_value = _mock_response(204)
    result = notifier.send("Job Failed", "daily-backup missed its run")
    assert result is True


@patch("cron_watcher.notifiers.hipchat_notifier.requests.post")
def test_send_posts_correct_payload(mock_post, notifier):
    mock_post.return_value = _mock_response(204)
    notifier.send("Alert", "Something went wrong")
    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert "Alert" in payload["message"]
    assert "Something went wrong" in payload["message"]
    assert payload["color"] == "red"
    assert payload["notify"] is True


@patch("cron_watcher.notifiers.hipchat_notifier.requests.post")
def test_send_returns_false_on_http_error(mock_post, notifier):
    mock_post.return_value = _mock_response(401)
    result = notifier.send("Alert", "body")
    assert result is False


@patch("cron_watcher.notifiers.hipchat_notifier.requests.post")
def test_send_returns_false_on_request_error(mock_post, notifier):
    mock_post.side_effect = requests.ConnectionError("unreachable")
    result = notifier.send("Alert", "body")
    assert result is False


@patch("cron_watcher.notifiers.hipchat_notifier.requests.post")
def test_send_uses_correct_url(mock_post, notifier):
    mock_post.return_value = _mock_response(204)
    notifier.send("Subject", "Body")
    url = mock_post.call_args[0][0]
    assert "123456" in url
    assert "notification" in url
    assert url.startswith("https://api.hipchat.com")


@patch("cron_watcher.notifiers.hipchat_notifier.requests.post")
def test_send_uses_bearer_auth(mock_post, notifier):
    mock_post.return_value = _mock_response(204)
    notifier.send("Subject", "Body")
    headers = mock_post.call_args[1]["headers"]
    assert headers["Authorization"] == "Bearer test-token"
