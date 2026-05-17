import json
from io import BytesIO
from unittest.mock import patch, MagicMock
import pytest
from cron_watcher.notifiers.twilio_notifier import TwilioConfig, TwilioNotifier


@pytest.fixture
def twilio_config():
    return TwilioConfig(
        account_sid="ACtest123",
        auth_token="secret_token",
        from_number="+15550001111",
        to_number="+15559998888",
    )


@pytest.fixture
def notifier(twilio_config):
    return TwilioNotifier(twilio_config)


def _mock_response(status=201, body=None):
    body = body or {"sid": "SMabc", "status": "queued"}
    mock = MagicMock()
    mock.status = status
    mock.read.return_value = json.dumps(body).encode()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


def test_send_returns_true_on_success(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response(201)):
        result = notifier.send("Job failed", "backup_job missed its run")
    assert result is True


def test_send_returns_false_on_http_error(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response(500)):
        result = notifier.send("Job failed", "backup_job missed its run")
    assert result is False


def test_send_returns_false_on_exception(notifier):
    with patch("urllib.request.urlopen", side_effect=Exception("network error")):
        result = notifier.send("Job failed", "backup_job missed its run")
    assert result is False


def test_send_posts_correct_payload(notifier):
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["data"] = req.data
        captured["headers"] = dict(req.headers)
        return _mock_response(201)

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        notifier.send("Alert", "Something went wrong")

    decoded = captured["data"].decode()
    assert "From=%2B15550001111" in decoded
    assert "To=%2B15559998888" in decoded
    assert "Body=" in decoded


def test_send_uses_basic_auth(notifier):
    import base64
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["auth"] = req.get_header("Authorization")
        return _mock_response(201)

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        notifier.send("Alert", "msg")

    expected = base64.b64encode(b"ACtest123:secret_token").decode()
    assert captured["auth"] == f"Basic {expected}"
