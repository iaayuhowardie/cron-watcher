from unittest.mock import MagicMock, patch

import pytest
import requests

from cron_watcher.notifiers.pushbullet_notifier import PushbulletConfig, PushbulletNotifier


@pytest.fixture
def pushbullet_config() -> PushbulletConfig:
    return PushbulletConfig(access_token="test-token")


@pytest.fixture
def notifier(pushbullet_config: PushbulletConfig) -> PushbulletNotifier:
    return PushbulletNotifier(config=pushbullet_config)


def _mock_response(status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)
    else:
        mock.raise_for_status.return_value = None
    return mock


def test_send_returns_true_on_success(notifier: PushbulletNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)):
        result = notifier.send("Test Subject", "Test Body")
    assert result is True


def test_send_posts_correct_payload(notifier: PushbulletNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Alert", "Job failed")
    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["type"] == "note"
    assert payload["title"] == "Alert"
    assert payload["body"] == "Job failed"


def test_send_includes_access_token_header(notifier: PushbulletNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Alert", "Body")
    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["Access-Token"] == "test-token"


def test_send_returns_false_on_request_error(notifier: PushbulletNotifier) -> None:
    with patch("requests.post", side_effect=requests.ConnectionError("timeout")):
        result = notifier.send("Alert", "Body")
    assert result is False


def test_send_returns_false_on_http_error(notifier: PushbulletNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(401)):
        result = notifier.send("Alert", "Body")
    assert result is False


def test_send_with_device_iden() -> None:
    config = PushbulletConfig(access_token="token", device_iden="abc123")
    n = PushbulletNotifier(config=config)
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        n.send("Alert", "Body")
    _, kwargs = mock_post.call_args
    assert kwargs["json"]["device_iden"] == "abc123"


def test_send_with_channel_tag() -> None:
    config = PushbulletConfig(access_token="token", channel_tag="ops-alerts")
    n = PushbulletNotifier(config=config)
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        n.send("Alert", "Body")
    _, kwargs = mock_post.call_args
    assert kwargs["json"]["channel_tag"] == "ops-alerts"
