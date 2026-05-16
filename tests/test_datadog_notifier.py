import pytest
import requests
from unittest.mock import MagicMock, patch

from cron_watcher.notifiers.datadog_notifier import DatadogConfig, DatadogNotifier


@pytest.fixture
def datadog_config():
    return DatadogConfig(
        api_key="test-api-key",
        app_key="test-app-key",
        host="myhost",
        tags=["env:prod", "service:cron"],
        timeout=5,
    )


@pytest.fixture
def notifier(datadog_config):
    return DatadogNotifier(datadog_config)


def _mock_response(status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)
    else:
        mock.raise_for_status.return_value = None
    return mock


@patch("cron_watcher.notifiers.datadog_notifier.requests.post")
def test_send_returns_true_on_success(mock_post, notifier):
    mock_post.return_value = _mock_response(200)
    result = notifier.send("Job failed", "backup job did not run")
    assert result is True


@patch("cron_watcher.notifiers.datadog_notifier.requests.post")
def test_send_posts_correct_payload(mock_post, notifier):
    mock_post.return_value = _mock_response(200)
    notifier.send("Job failed", "details here")
    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["title"] == "Job failed"
    assert payload["text"] == "details here"
    assert payload["alert_type"] == "error"
    assert "host:myhost" in payload["tags"]
    assert "env:prod" in payload["tags"]


@patch("cron_watcher.notifiers.datadog_notifier.requests.post")
def test_send_includes_api_key_header(mock_post, notifier):
    mock_post.return_value = _mock_response(200)
    notifier.send("s", "b")
    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["DD-API-KEY"] == "test-api-key"
    assert kwargs["headers"]["DD-APPLICATION-KEY"] == "test-app-key"


@patch("cron_watcher.notifiers.datadog_notifier.requests.post")
def test_send_returns_false_on_request_error(mock_post, notifier):
    mock_post.side_effect = requests.RequestException("connection error")
    result = notifier.send("Job failed", "body")
    assert result is False


@patch("cron_watcher.notifiers.datadog_notifier.requests.post")
def test_send_returns_false_on_http_error(mock_post, notifier):
    mock_post.return_value = _mock_response(403)
    result = notifier.send("Job failed", "body")
    assert result is False


@patch("cron_watcher.notifiers.datadog_notifier.requests.post")
def test_send_without_optional_fields(mock_post):
    config = DatadogConfig(api_key="key-only")
    n = DatadogNotifier(config)
    mock_post.return_value = _mock_response(200)
    result = n.send("title", "body")
    assert result is True
    _, kwargs = mock_post.call_args
    assert "DD-APPLICATION-KEY" not in kwargs["headers"]
    assert "host:" not in " ".join(kwargs["json"]["tags"])
