import pytest
from unittest.mock import MagicMock, patch
import requests
from cron_watcher.notifiers import get_notifier


def _mock_response(json_data=None):
    mock = MagicMock()
    mock.status_code = 200
    mock.raise_for_status.return_value = None
    mock.json.return_value = json_data or {"code": 0}
    return mock


def test_get_notifier_returns_lark_notifier():
    notifier = get_notifier("lark", {"webhook_url": "https://open.feishu.cn/hook/abc"})
    assert notifier is not None
    from cron_watcher.notifiers.lark_notifier import LarkNotifier
    assert isinstance(notifier, LarkNotifier)


def test_get_notifier_lark_case_insensitive():
    notifier = get_notifier("LARK", {"webhook_url": "https://open.feishu.cn/hook/abc"})
    assert notifier is not None


def test_get_notifier_lark_send_returns_true():
    notifier = get_notifier("lark", {"webhook_url": "https://open.feishu.cn/hook/abc"})
    with patch("requests.post", return_value=_mock_response({"code": 0})):
        result = notifier.send("Test subject", "Test body")
    assert result is True


def test_get_notifier_returns_bearychat_notifier():
    notifier = get_notifier(
        "bearychat", {"webhook_url": "https://hook.bearychat.com/abc"}
    )
    assert notifier is not None
    from cron_watcher.notifiers.bearychat_notifier import BearyChatNotifier
    assert isinstance(notifier, BearyChatNotifier)


def test_get_notifier_bearychat_case_insensitive():
    notifier = get_notifier(
        "BearyChat", {"webhook_url": "https://hook.bearychat.com/abc"}
    )
    assert notifier is not None


def test_get_notifier_bearychat_send_returns_true():
    notifier = get_notifier(
        "bearychat", {"webhook_url": "https://hook.bearychat.com/abc"}
    )
    with patch("requests.post", return_value=_mock_response()):
        result = notifier.send("Missed run", "job_x missed")
    assert result is True
