import pytest
import requests
from unittest.mock import MagicMock, patch

from cron_watcher.notifiers.gotify_notifier import GotifyConfig, GotifyNotifier


@pytest.fixture
def gotify_config():
    return GotifyConfig(
        url="https://gotify.example.com",
        token="test-app-token",
        priority=7,
    )


@pytest.fixture
def notifier(gotify_config):
    return GotifyNotifier(gotify_config)


def _mock_response(status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)
    else:
        mock.raise_for_status.return_value = None
    return mock


@patch("cron_watcher.notifiers.gotify_notifier.requests.post")
def test_send_returns_true_on_success(mock_post, notifier):
    mock_post.return_value = _mock_response(200)
    result = notifier.send("Test Subject", "Test message body")
    assert result is True


@patch("cron_watcher.notifiers.gotify_notifier.requests.post")
def test_send_posts_correct_payload(mock_post, notifier, gotify_config):
    mock_post.return_value = _mock_response(200)
    notifier.send("Alert: job failed", "Details here")
    _, kwargs = mock_post.call_args
    assert kwargs["json"]["title"] == "Alert: job failed"
    assert kwargs["json"]["message"] == "Details here"
    assert kwargs["json"]["priority"] == gotify_config.priority


@patch("cron_watcher.notifiers.gotify_notifier.requests.post")
def test_send_uses_correct_endpoint(mock_post, notifier, gotify_config):
    mock_post.return_value = _mock_response(200)
    notifier.send("Subject", "Body")
    url_called = mock_post.call_args[0][0]
    assert url_called == gotify_config.url.rstrip("/") + "/message"


@patch("cron_watcher.notifiers.gotify_notifier.requests.post")
def test_send_includes_auth_header(mock_post, notifier, gotify_config):
    mock_post.return_value = _mock_response(200)
    notifier.send("Subject", "Body")
    headers = mock_post.call_args[1]["headers"]
    assert headers["X-Gotify-Key"] == gotify_config.token


@patch("cron_watcher.notifiers.gotify_notifier.requests.post")
def test_send_returns_false_on_request_error(mock_post, notifier):
    mock_post.side_effect = requests.ConnectionError("unreachable")
    result = notifier.send("Subject", "Body")
    assert result is False


@patch("cron_watcher.notifiers.gotify_notifier.requests.post")
def test_send_returns_false_on_http_error(mock_post, notifier):
    mock_post.return_value = _mock_response(401)
    result = notifier.send("Subject", "Body")
    assert result is False


def test_default_priority():
    config = GotifyConfig(url="https://gotify.example.com", token="tok")
    assert config.priority == 5
