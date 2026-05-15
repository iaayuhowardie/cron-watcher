import pytest
from unittest.mock import MagicMock, patch

from cron_watcher.notifiers.slack_notifier import SlackConfig, SlackNotifier


@pytest.fixture
def slack_config() -> SlackConfig:
    return SlackConfig(
        webhook_url="https://hooks.slack.com/services/TEST/WEBHOOK",
        channel="#alerts",
        username="cron-watcher",
        icon_emoji=":warning:",
    )


@pytest.fixture
def notifier(slack_config: SlackConfig) -> SlackNotifier:
    return SlackNotifier(config=slack_config)


def test_send_returns_true_on_success(notifier: SlackNotifier) -> None:
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None

    with patch("requests.post", return_value=mock_response) as mock_post:
        result = notifier.send("Job failed", "backup-job did not complete")

    assert result is True
    mock_post.assert_called_once()


def test_send_posts_correct_payload(notifier: SlackNotifier) -> None:
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None

    with patch("requests.post", return_value=mock_response) as mock_post:
        notifier.send("Missed run", "daily-report was not executed")

    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["username"] == "cron-watcher"
    assert payload["channel"] == "#alerts"
    assert payload["attachments"][0]["title"] == "Missed run"
    assert payload["attachments"][0]["text"] == "daily-report was not executed"


def test_send_returns_false_on_request_error(notifier: SlackNotifier) -> None:
    import requests

    with patch("requests.post", side_effect=requests.RequestException("timeout")):
        result = notifier.send("Job failed", "something went wrong")

    assert result is False


def test_send_without_channel() -> None:
    config = SlackConfig(webhook_url="https://hooks.slack.com/services/NO/CHANNEL")
    notifier = SlackNotifier(config=config)
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None

    with patch("requests.post", return_value=mock_response) as mock_post:
        result = notifier.send("Alert", "body text")

    assert result is True
    _, kwargs = mock_post.call_args
    assert "channel" not in kwargs["json"]


def test_send_returns_false_on_http_error(notifier: SlackNotifier) -> None:
    import requests

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("403 Forbidden")

    with patch("requests.post", return_value=mock_response):
        result = notifier.send("Job failed", "access denied")

    assert result is False
