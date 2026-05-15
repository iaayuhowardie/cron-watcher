import pytest
import requests
from unittest.mock import MagicMock, patch
from cron_watcher.notifiers.victorops_notifier import VictorOpsConfig, VictorOpsNotifier


@pytest.fixture
def victorops_config():
    return VictorOpsConfig(
        routing_key="test-route",
        rest_endpoint_url="https://alert.victorops.com/integrations/generic/12345/alert/token",
        entity_display_name="cron-watcher-test",
        timeout=5,
    )


@pytest.fixture
def notifier(victorops_config):
    return VictorOpsNotifier(victorops_config)


def _mock_response(status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)
    else:
        mock.raise_for_status.return_value = None
    return mock


def test_send_returns_true_on_success(notifier):
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        result = notifier.send("Job missed", "backup-job did not run")
    assert result is True
    mock_post.assert_called_once()


def test_send_posts_correct_payload(notifier, victorops_config):
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Job failed", "nightly-sync failed with exit code 1")
    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["message_type"] == "CRITICAL"
    assert payload["entity_display_name"] == victorops_config.entity_display_name
    assert "nightly-sync failed" in payload["state_message"]
    assert payload["monitoring_tool"] == "cron-watcher"


def test_send_uses_correct_url(notifier, victorops_config):
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Job missed", "details")
    url = mock_post.call_args[0][0]
    assert victorops_config.routing_key in url
    assert victorops_config.rest_endpoint_url.rstrip("/") in url


def test_send_returns_false_on_request_error(notifier):
    with patch("requests.post", side_effect=requests.ConnectionError("unreachable")):
        result = notifier.send("Job missed", "details")
    assert result is False


def test_send_returns_false_on_http_error(notifier):
    with patch("requests.post", return_value=_mock_response(500)):
        result = notifier.send("Job missed", "details")
    assert result is False


def test_send_uses_configured_timeout(notifier, victorops_config):
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Job missed", "details")
    _, kwargs = mock_post.call_args
    assert kwargs["timeout"] == victorops_config.timeout
