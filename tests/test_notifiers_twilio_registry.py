import json
from unittest.mock import patch, MagicMock
import pytest
from cron_watcher.notifiers import get_notifier


def _mock_response(status=201):
    body = {"sid": "SMabc", "status": "queued"}
    mock = MagicMock()
    mock.status = status
    mock.read.return_value = json.dumps(body).encode()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


def test_get_notifier_returns_twilio_notifier():
    from cron_watcher.notifiers.twilio_notifier import TwilioNotifier
    notifier = get_notifier("twilio", {
        "account_sid": "ACtest",
        "auth_token": "token",
        "from_number": "+15550001111",
        "to_number": "+15559998888",
    })
    assert isinstance(notifier, TwilioNotifier)


def test_get_notifier_twilio_case_insensitive():
    from cron_watcher.notifiers.twilio_notifier import TwilioNotifier
    notifier = get_notifier("TWILIO", {
        "account_sid": "ACtest",
        "auth_token": "token",
        "from_number": "+15550001111",
        "to_number": "+15559998888",
    })
    assert isinstance(notifier, TwilioNotifier)


def test_get_notifier_twilio_send_returns_true():
    notifier = get_notifier("twilio", {
        "account_sid": "ACtest",
        "auth_token": "token",
        "from_number": "+15550001111",
        "to_number": "+15559998888",
    })
    with patch("urllib.request.urlopen", return_value=_mock_response(201)):
        result = notifier.send("Test subject", "Test body")
    assert result is True


def test_get_notifier_twilio_with_custom_timeout():
    from cron_watcher.notifiers.twilio_notifier import TwilioNotifier
    notifier = get_notifier("twilio", {
        "account_sid": "ACtest",
        "auth_token": "token",
        "from_number": "+15550001111",
        "to_number": "+15559998888",
        "timeout": 30,
    })
    assert isinstance(notifier, TwilioNotifier)
    assert notifier.config.timeout == 30
