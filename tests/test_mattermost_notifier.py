from unittest.mock import MagicMock, patch

import pytest
import requests

from cron_watcher.notifiers.mattermost_notifier import MattermostConfig, MattermostNotifier


@pytest.fixture
def mattermost_config() -> MattermostConfig:
    return MattermostConfig(
        webhook_url="https://mattermost.example.com/hooks/abc123",
        channel="#alerts",
        username="cron-watcher",
        icon_emoji=":warning:",
    )


@pytest.fixture
def notifier(mattermost_config: MattermostConfig) -> MattermostNotifier:
    return MattermostNotifier(mattermost_config)


def _mock_response(status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)
    else:
        mock.raise_for_status.return_value = None
    return mock


def test_send_returns_true_on_success(notifier: MattermostNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        result = notifier.send("Job missed", "backup-job did not run")
    assert result is True
    mock_post.assert_called_once()


def test_send_posts_correct_payload(notifier: MattermostNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Alert", "Something went wrong")
    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert "**Alert**" in payload["text"]
    assert "Something went wrong" in payload["text"]
    assert payload["channel"] == "#alerts"
    assert payload["username"] == "cron-watcher"
    assert payload["icon_emoji"] == ":warning:"


def test_send_returns_false_on_request_error(notifier: MattermostNotifier) -> None:
    with patch("requests.post", side_effect=requests.ConnectionError("unreachable")):
        result = notifier.send("Job failed", "error details")
    assert result is False


def test_send_returns_false_on_http_error(notifier: MattermostNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(500)):
        result = notifier.send("Job failed", "error details")
    assert result is False


def test_send_without_channel() -> None:
    config = MattermostConfig(webhook_url="https://mattermost.example.com/hooks/xyz")
    notifier = MattermostNotifier(config)
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        result = notifier.send("Test", "No channel specified")
    assert result is True
    payload = mock_post.call_args[1]["json"]
    assert "channel" not in payload
