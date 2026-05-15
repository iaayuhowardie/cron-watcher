from unittest.mock import MagicMock, patch

import pytest
import requests

from cron_watcher.notifiers.pagerduty_notifier import PagerDutyConfig, PagerDutyNotifier


@pytest.fixture
def pagerduty_config() -> PagerDutyConfig:
    return PagerDutyConfig(
        integration_key="test-integration-key-abc123",
        severity="error",
        source="cron-watcher-test",
        timeout=5,
    )


@pytest.fixture
def notifier(pagerduty_config: PagerDutyConfig) -> PagerDutyNotifier:
    return PagerDutyNotifier(config=pagerduty_config)


def _mock_response(status_code: int = 202) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock
        )
    else:
        mock.raise_for_status.return_value = None
    return mock


@patch("cron_watcher.notifiers.pagerduty_notifier.requests.post")
def test_send_returns_true_on_success(mock_post, notifier):
    mock_post.return_value = _mock_response(202)
    result = notifier.send("backup job missed", {"job": "backup"})
    assert result is True


@patch("cron_watcher.notifiers.pagerduty_notifier.requests.post")
def test_send_posts_correct_payload(mock_post, notifier, pagerduty_config):
    mock_post.return_value = _mock_response(202)
    notifier.send("test summary", {"key": "value"})

    _, kwargs = mock_post.call_args
    payload = kwargs["json"]

    assert payload["routing_key"] == pagerduty_config.integration_key
    assert payload["event_action"] == "trigger"
    assert payload["payload"]["summary"] == "test summary"
    assert payload["payload"]["severity"] == pagerduty_config.severity
    assert payload["payload"]["source"] == pagerduty_config.source
    assert payload["payload"]["custom_details"] == {"key": "value"}


@patch("cron_watcher.notifiers.pagerduty_notifier.requests.post")
def test_send_returns_false_on_http_error(mock_post, notifier):
    mock_post.return_value = _mock_response(400)
    result = notifier.send("alert", {})
    assert result is False


@patch("cron_watcher.notifiers.pagerduty_notifier.requests.post")
def test_send_returns_false_on_request_exception(mock_post, notifier):
    mock_post.side_effect = requests.exceptions.ConnectionError("unreachable")
    result = notifier.send("alert", {})
    assert result is False


@patch("cron_watcher.notifiers.pagerduty_notifier.requests.post")
def test_send_without_details(mock_post, notifier):
    mock_post.return_value = _mock_response(202)
    result = notifier.send("no details alert")
    assert result is True
    _, kwargs = mock_post.call_args
    assert kwargs["json"]["payload"]["custom_details"] == {}
