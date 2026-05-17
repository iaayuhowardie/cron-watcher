import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import RequestException

from cron_watcher.notifiers.campfire_notifier import CampfireConfig, CampfireNotifier


@pytest.fixture
def campfire_config():
    return CampfireConfig(
        account="mycompany",
        token="abc123token",
        room_id="987654",
    )


@pytest.fixture
def notifier(campfire_config):
    return CampfireNotifier(campfire_config)


def _mock_response(status_code=201):
    mock = MagicMock()
    mock.status_code = status_code
    mock.raise_for_status = MagicMock()
    return mock


@patch("cron_watcher.notifiers.campfire_notifier.requests")
def test_send_returns_true_on_success(mock_requests, notifier):
    mock_requests.post.return_value = _mock_response(201)
    mock_requests.RequestException = RequestException
    result = notifier.send("Job failed", "backup_job missed its run")
    assert result is True


@patch("cron_watcher.notifiers.campfire_notifier.requests")
def test_send_posts_correct_url(mock_requests, notifier):
    mock_requests.post.return_value = _mock_response(201)
    mock_requests.RequestException = RequestException
    notifier.send("Alert", "details")
    call_url = mock_requests.post.call_args[0][0]
    assert "mycompany.campfirenow.com" in call_url
    assert "987654" in call_url
    assert call_url.startswith("https://")


@patch("cron_watcher.notifiers.campfire_notifier.requests")
def test_send_posts_correct_payload(mock_requests, notifier):
    mock_requests.post.return_value = _mock_response(201)
    mock_requests.RequestException = RequestException
    notifier.send("Subject", "Body text")
    kwargs = mock_requests.post.call_args[1]
    payload = kwargs["json"]
    assert payload["message"]["type"] == "TextMessage"
    assert "Subject" in payload["message"]["body"]
    assert "Body text" in payload["message"]["body"]


@patch("cron_watcher.notifiers.campfire_notifier.requests")
def test_send_returns_false_on_request_error(mock_requests, notifier):
    mock_requests.post.side_effect = RequestException("connection refused")
    mock_requests.RequestException = RequestException
    result = notifier.send("Alert", "details")
    assert result is False


@patch("cron_watcher.notifiers.campfire_notifier.requests")
def test_send_uses_token_auth(mock_requests, notifier):
    mock_requests.post.return_value = _mock_response(201)
    mock_requests.RequestException = RequestException
    notifier.send("Alert", "details")
    kwargs = mock_requests.post.call_args[1]
    assert kwargs["auth"] == ("abc123token", "x")


@patch("cron_watcher.notifiers.campfire_notifier.requests")
def test_send_uses_http_when_ssl_disabled(mock_requests):
    config = CampfireConfig(
        account="mycompany",
        token="abc123token",
        room_id="987654",
        ssl=False,
    )
    notifier = CampfireNotifier(config)
    mock_requests.post.return_value = _mock_response(201)
    mock_requests.RequestException = RequestException
    notifier.send("Alert", "details")
    call_url = mock_requests.post.call_args[0][0]
    assert call_url.startswith("http://")
