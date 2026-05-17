from unittest.mock import MagicMock, patch

import pytest
import requests

from cron_watcher.notifiers.mailgun_notifier import MailgunConfig, MailgunNotifier


@pytest.fixture
def mailgun_config():
    return MailgunConfig(
        api_key="key-abc123",
        domain="mg.example.com",
        from_address="alerts@mg.example.com",
        to_addresses=["ops@example.com", "dev@example.com"],
    )


@pytest.fixture
def notifier(mailgun_config):
    return MailgunNotifier(mailgun_config)


def _mock_response(status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError(
            response=mock
        )
    else:
        mock.raise_for_status.return_value = None
    return mock


def test_send_returns_true_on_success(notifier):
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        result = notifier.send("Job missed", "backup-job did not run")
    assert result is True
    mock_post.assert_called_once()


def test_send_posts_to_correct_url(notifier, mailgun_config):
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Test", "body")
    call_args = mock_post.call_args
    expected_url = "https://api.mailgun.net/v3/mg.example.com/messages"
    assert call_args[0][0] == expected_url


def test_send_uses_api_key_auth(notifier, mailgun_config):
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Test", "body")
    call_kwargs = mock_post.call_args[1]
    assert call_kwargs["auth"] == ("api", mailgun_config.api_key)


def test_send_includes_subject_prefix(notifier):
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Job failed", "details here")
    payload = mock_post.call_args[1]["data"]
    assert payload["subject"] == "[cron-watcher] Job failed"


def test_send_includes_all_recipients(notifier, mailgun_config):
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Alert", "message")
    payload = mock_post.call_args[1]["data"]
    assert "ops@example.com" in payload["to"]
    assert "dev@example.com" in payload["to"]


def test_send_returns_false_on_http_error(notifier):
    with patch("requests.post", return_value=_mock_response(401)):
        result = notifier.send("Alert", "message")
    assert result is False


def test_send_returns_false_on_request_error(notifier):
    with patch(
        "requests.post", side_effect=requests.ConnectionError("unreachable")
    ):
        result = notifier.send("Alert", "message")
    assert result is False


def test_send_with_custom_api_base_url():
    config = MailgunConfig(
        api_key="key-eu",
        domain="mg.eu.example.com",
        from_address="alerts@mg.eu.example.com",
        to_addresses=["team@example.com"],
        api_base_url="https://api.eu.mailgun.net/v3",
    )
    notifier = MailgunNotifier(config)
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        result = notifier.send("EU alert", "body")
    assert result is True
    url = mock_post.call_args[0][0]
    assert url.startswith("https://api.eu.mailgun.net/v3")
