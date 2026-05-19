from unittest.mock import MagicMock, patch

import pytest
import requests

from cron_watcher.notifiers.clicksend_notifier import ClickSendConfig, ClickSendNotifier


@pytest.fixture
def clicksend_config() -> ClickSendConfig:
    return ClickSendConfig(
        username="testuser",
        api_key="testapikey",
        from_number="+10000000000",
        to_number="+19999999999",
    )


@pytest.fixture
def notifier(clicksend_config: ClickSendConfig) -> ClickSendNotifier:
    return ClickSendNotifier(clicksend_config)


def _mock_response(status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)
    else:
        mock.raise_for_status.return_value = None
    return mock


def test_send_returns_true_on_success(notifier: ClickSendNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)):
        result = notifier.send("Job failed", "backup_job did not run")
    assert result is True


def test_send_returns_false_on_http_error(notifier: ClickSendNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(401)):
        result = notifier.send("Job failed", "backup_job did not run")
    assert result is False


def test_send_returns_false_on_request_error(notifier: ClickSendNotifier) -> None:
    with patch("requests.post", side_effect=requests.ConnectionError("timeout")):
        result = notifier.send("Job failed", "backup_job did not run")
    assert result is False


def test_send_posts_correct_payload(notifier: ClickSendNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Alert", "some message")
    call_kwargs = mock_post.call_args
    payload = call_kwargs.kwargs["json"]
    assert len(payload["messages"]) == 1
    msg = payload["messages"][0]
    assert msg["to"] == "+19999999999"
    assert msg["from"] == "+10000000000"
    assert "Alert" in msg["body"]
    assert "some message" in msg["body"]


def test_send_uses_basic_auth(notifier: ClickSendNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Alert", "msg")
    auth = mock_post.call_args.kwargs["auth"]
    assert auth.username == "testuser"
    assert auth.password == "testapikey"


def test_send_respects_timeout(clicksend_config: ClickSendConfig) -> None:
    clicksend_config.timeout = 5
    notifier = ClickSendNotifier(clicksend_config)
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Alert", "msg")
    assert mock_post.call_args.kwargs["timeout"] == 5
