import json
from unittest.mock import MagicMock, patch
import pytest

from cron_watcher.notifiers import get_notifier
from cron_watcher.notifiers.line_notifier import LineNotifier


def _mock_response():
    mock = MagicMock()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


def test_get_notifier_returns_line_notifier():
    cfg = {
        "channel_access_token": "tok",
        "to": "U123",
    }
    notifier = get_notifier("line", cfg)
    assert isinstance(notifier, LineNotifier)


def test_get_notifier_line_case_insensitive():
    cfg = {
        "channel_access_token": "tok",
        "to": "U123",
    }
    assert isinstance(get_notifier("LINE", cfg), LineNotifier)
    assert isinstance(get_notifier("Line", cfg), LineNotifier)


def test_get_notifier_line_send_returns_true():
    cfg = {
        "channel_access_token": "tok",
        "to": "U123",
    }
    notifier = get_notifier("line", cfg)
    with patch("urllib.request.urlopen", return_value=_mock_response()):
        result = notifier.send("Test subject", "Test message")
    assert result is True


def test_get_notifier_line_with_custom_timeout():
    cfg = {
        "channel_access_token": "tok",
        "to": "G987",
        "timeout": 30,
    }
    notifier = get_notifier("line", cfg)
    assert isinstance(notifier, LineNotifier)
    assert notifier.config.timeout == 30
    assert notifier.config.to == "G987"
