import json
from unittest.mock import MagicMock, patch
import urllib.error
import pytest

from cron_watcher.notifiers.line_notifier import LineConfig, LineNotifier


@pytest.fixture
def line_config():
    return LineConfig(
        channel_access_token="test-channel-access-token",
        to="U1234567890abcdef",
    )


@pytest.fixture
def notifier(line_config):
    return LineNotifier(line_config)


def _mock_response():
    mock = MagicMock()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


def test_send_returns_true_on_success(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response()):
        result = notifier.send("Job failed", "backup_job missed its schedule")
    assert result is True


def test_send_returns_false_on_request_error(notifier):
    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError("connection refused"),
    ):
        result = notifier.send("Job failed", "backup_job missed its schedule")
    assert result is False


def test_send_posts_correct_payload(notifier):
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["data"] = json.loads(req.data.decode("utf-8"))
        captured["auth"] = req.get_header("Authorization")
        return _mock_response()

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        notifier.send("Alert", "Something went wrong")

    assert captured["url"] == LineNotifier.API_URL
    assert captured["data"]["to"] == "U1234567890abcdef"
    assert len(captured["data"]["messages"]) == 1
    assert captured["data"]["messages"][0]["type"] == "text"
    assert "Alert" in captured["data"]["messages"][0]["text"]
    assert "Something went wrong" in captured["data"]["messages"][0]["text"]
    assert captured["auth"] == "Bearer test-channel-access-token"


def test_send_uses_configured_timeout(notifier):
    notifier.config.timeout = 5
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["timeout"] = timeout
        return _mock_response()

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        notifier.send("Alert", "msg")

    assert captured["timeout"] == 5


def test_send_includes_subject_and_message_in_text(notifier):
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["data"] = json.loads(req.data.decode("utf-8"))
        return _mock_response()

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        notifier.send("SUBJECT", "BODY")

    text = captured["data"]["messages"][0]["text"]
    assert "SUBJECT" in text
    assert "BODY" in text
