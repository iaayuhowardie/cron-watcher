import json
from unittest.mock import MagicMock, patch
import urllib.error
import pytest
from cron_watcher.notifiers.freshstatus_notifier import FreshstatusConfig, FreshstatusNotifier


@pytest.fixture
def freshstatus_config():
    return FreshstatusConfig(
        api_key="test-api-key",
        monitor_id="mon-789",
    )


@pytest.fixture
def notifier(freshstatus_config):
    return FreshstatusNotifier(freshstatus_config)


def _mock_response():
    mock = MagicMock()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


def test_send_returns_true_on_success(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response()):
        result = notifier.send("subject", "body")
    assert result is True


def test_send_posts_correct_payload(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response()) as mock_open:
        notifier.send("Job failed", "Details")
    req = mock_open.call_args[0][0]
    payload = json.loads(req.data.decode())
    assert payload["title"] == "Job failed"
    assert payload["description"] == "Details"
    assert "mon-789" in payload["monitor_ids"]


def test_send_uses_basic_auth_header(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response()) as mock_open:
        notifier.send("s", "b")
    req = mock_open.call_args[0][0]
    assert req.get_header("Authorization") == "Basic test-api-key"


def test_send_returns_false_on_url_error(notifier):
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
        result = notifier.send("s", "b")
    assert result is False


def test_send_posts_to_incidents_endpoint(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response()) as mock_open:
        notifier.send("s", "b")
    req = mock_open.call_args[0][0]
    assert req.full_url.endswith("/incidents/")
