import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import RequestException
from cron_watcher.notifiers.zulip_notifier import ZulipConfig, ZulipNotifier


@pytest.fixture
def zulip_config():
    return ZulipConfig(
        site="https://myorg.zulipchat.com",
        email="bot@myorg.zulipchat.com",
        api_key="supersecretkey",
        stream="alerts",
        topic="cron-watcher alerts",
    )


@pytest.fixture
def notifier(zulip_config):
    return ZulipNotifier(zulip_config)


def _mock_response(status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        from requests.exceptions import HTTPError
        mock.raise_for_status.side_effect = HTTPError()
    else:
        mock.raise_for_status.return_value = None
    return mock


def test_send_returns_true_on_success(notifier):
    with patch("requests.post", return_value=_mock_response(200)):
        assert notifier.send("Test Subject", "Test message") is True


def test_send_returns_false_on_request_error(notifier):
    with patch("requests.post", side_effect=RequestException("connection error")):
        assert notifier.send("Test Subject", "Test message") is False


def test_send_returns_false_on_http_error(notifier):
    with patch("requests.post", return_value=_mock_response(403)):
        assert notifier.send("Test Subject", "Test message") is False


def test_send_posts_correct_payload(notifier, zulip_config):
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Alert", "Job failed")
        call_kwargs = mock_post.call_args
        data = call_kwargs[1]["data"]
        assert data["type"] == "stream"
        assert data["to"] == zulip_config.stream
        assert data["topic"] == zulip_config.topic
        assert "Alert" in data["content"]
        assert "Job failed" in data["content"]


def test_send_uses_correct_auth(notifier, zulip_config):
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Alert", "Job failed")
        call_kwargs = mock_post.call_args
        auth = call_kwargs[1]["auth"]
        assert auth == (zulip_config.email, zulip_config.api_key)


def test_send_uses_correct_url(notifier, zulip_config):
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Alert", "Job failed")
        call_args = mock_post.call_args
        url = call_args[0][0]
        assert url == "https://myorg.zulipchat.com/api/v1/messages"
