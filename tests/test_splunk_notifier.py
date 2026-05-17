import pytest
import requests
from unittest.mock import MagicMock, patch
from cron_watcher.notifiers.splunk_notifier import SplunkConfig, SplunkNotifier


@pytest.fixture
def splunk_config():
    return SplunkConfig(
        hec_url="https://splunk.example.com:8088/services/collector/event",
        token="test-hec-token",
        index="cron_index",
        source="cron-watcher",
        sourcetype="cron_alert",
    )


@pytest.fixture
def notifier(splunk_config):
    return SplunkNotifier(splunk_config)


def _mock_response(status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    if status_code >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError(
            response=resp
        )
    else:
        resp.raise_for_status.return_value = None
    return resp


def test_send_returns_true_on_success(notifier):
    with patch.object(notifier._session, "post", return_value=_mock_response(200)) as mock_post:
        result = notifier.send("Job missed", "backup-job did not run")
    assert result is True
    mock_post.assert_called_once()


def test_send_posts_correct_payload(notifier):
    with patch.object(notifier._session, "post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Job failed", "nightly-sync exited with code 1")
    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["index"] == "cron_index"
    assert payload["source"] == "cron-watcher"
    assert payload["sourcetype"] == "cron_alert"
    assert payload["event"]["subject"] == "Job failed"
    assert payload["event"]["message"] == "nightly-sync exited with code 1"


def test_send_returns_false_on_http_error(notifier):
    with patch.object(notifier._session, "post", return_value=_mock_response(403)):
        result = notifier.send("Job missed", "some job")
    assert result is False


def test_send_returns_false_on_connection_error(notifier):
    with patch.object(
        notifier._session, "post", side_effect=requests.ConnectionError("unreachable")
    ):
        result = notifier.send("Job missed", "some job")
    assert result is False


def test_send_uses_authorization_header(notifier):
    assert notifier._session.headers["Authorization"] == "Splunk test-hec-token"


def test_send_respects_verify_ssl_false():
    config = SplunkConfig(
        hec_url="https://splunk.local:8088/services/collector/event",
        token="abc",
        verify_ssl=False,
    )
    n = SplunkNotifier(config)
    with patch.object(n._session, "post", return_value=_mock_response(200)) as mock_post:
        n.send("test", "body")
    _, kwargs = mock_post.call_args
    assert kwargs["verify"] is False
