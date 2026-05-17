import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import RequestException
from cron_watcher.notifiers.googlechat_notifier import GoogleChatConfig, GoogleChatNotifier


@pytest.fixture
def googlechat_config() -> GoogleChatConfig:
    return GoogleChatConfig(
        webhook_url="https://chat.googleapis.com/v1/spaces/XXX/messages",
        timeout=5,
    )


@pytest.fixture
def notifier(googlechat_config: GoogleChatConfig) -> GoogleChatNotifier:
    return GoogleChatNotifier(googlechat_config)


def _mock_response(status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        from requests import HTTPError
        mock.raise_for_status.side_effect = HTTPError(response=mock)
    else:
        mock.raise_for_status.return_value = None
    return mock


def test_send_returns_true_on_success(notifier: GoogleChatNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)):
        assert notifier.send("Test Subject", "Test body") is True


def test_send_posts_correct_payload(notifier: GoogleChatNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Alert", "Job failed")
        _, kwargs = mock_post.call_args
        assert "*Alert*" in kwargs["json"]["text"]
        assert "Job failed" in kwargs["json"]["text"]


def test_send_returns_false_on_request_error(notifier: GoogleChatNotifier) -> None:
    with patch("requests.post", side_effect=RequestException("connection error")):
        assert notifier.send("Subject", "Body") is False


def test_send_returns_false_on_http_error(notifier: GoogleChatNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(400)):
        assert notifier.send("Subject", "Body") is False


def test_send_with_thread_key() -> None:
    config = GoogleChatConfig(
        webhook_url="https://chat.googleapis.com/v1/spaces/XXX/messages",
        thread_key="my-thread",
    )
    notifier = GoogleChatNotifier(config)
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Subject", "Body")
        _, kwargs = mock_post.call_args
        assert kwargs["params"]["threadKey"] == "my-thread"


def test_send_without_thread_key_omits_params(notifier: GoogleChatNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Subject", "Body")
        _, kwargs = mock_post.call_args
        assert kwargs.get("params") is None
