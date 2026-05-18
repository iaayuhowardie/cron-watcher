import json
from unittest.mock import MagicMock, patch
import pytest
from cron_watcher.notifiers.statuspage_notifier import StatuspageConfig, StatuspageNotifier


@pytest.fixture
def statuspage_config():
    return StatuspageConfig(
        api_key="test-api-key",
        page_id="abc123",
        component_id="comp456",
        incident_name="Test Incident",
    )


@pytest.fixture
def notifier(statuspage_config):
    return StatuspageNotifier(statuspage_config)


def _mock_response(status=201):
    mock = MagicMock()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    mock.status = status
    return mock


def test_send_returns_true_on_success(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response(201)):
        result = notifier.send("subject", "body")
    assert result is True


def test_send_posts_correct_payload(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response(201)) as mock_open:
        notifier.send("Alert: job failed", "Details here")
    call_args = mock_open.call_args
    req = call_args[0][0]
    payload = json.loads(req.data.decode())
    assert payload["incident"]["name"] == "Test Incident"
    assert payload["incident"]["status"] == "investigating"
    assert "Alert: job failed" in payload["incident"]["body"]
    assert payload["incident"]["component_ids"] == ["comp456"]


def test_send_uses_correct_url(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response(201)) as mock_open:
        notifier.send("s", "b")
    req = mock_open.call_args[0][0]
    assert "abc123" in req.full_url
    assert req.full_url.endswith("/incidents")


def test_send_uses_oauth_header(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response(201)) as mock_open:
        notifier.send("s", "b")
    req = mock_open.call_args[0][0]
    assert req.get_header("Authorization") == "OAuth test-api-key"


def test_send_returns_false_on_url_error(notifier):
    import urllib.error
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("connection refused")):
        result = notifier.send("s", "b")
    assert result is False


def test_send_includes_body_in_incident(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response(201)) as mock_open:
        notifier.send("Job missed", "Expected every 5 minutes")
    req = mock_open.call_args[0][0]
    payload = json.loads(req.data.decode())
    assert "Expected every 5 minutes" in payload["incident"]["body"]
