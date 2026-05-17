from unittest.mock import MagicMock, patch

import pytest
import requests

from cron_watcher.notifiers import get_notifier


def _mock_response(status_code=204):
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)
    else:
        mock.raise_for_status.return_value = None
    return mock


def test_get_notifier_returns_hipchat_notifier():
    from cron_watcher.notifiers.hipchat_notifier import HipChatNotifier

    notifier = get_notifier("hipchat", {"token": "tok", "room_id": "99"})
    assert isinstance(notifier, HipChatNotifier)


def test_get_notifier_hipchat_case_insensitive():
    from cron_watcher.notifiers.hipchat_notifier import HipChatNotifier

    notifier = get_notifier("HipChat", {"token": "tok", "room_id": "99"})
    assert isinstance(notifier, HipChatNotifier)


@patch("cron_watcher.notifiers.hipchat_notifier.requests.post")
def test_get_notifier_hipchat_send_returns_true(mock_post):
    mock_post.return_value = _mock_response(204)
    notifier = get_notifier("hipchat", {"token": "tok", "room_id": "99"})
    assert notifier is not None
    result = notifier.send("Test", "body")
    assert result is True


def test_get_notifier_hipchat_with_custom_color():
    from cron_watcher.notifiers.hipchat_notifier import HipChatNotifier

    notifier = get_notifier(
        "hipchat", {"token": "tok", "room_id": "99", "color": "yellow"}
    )
    assert isinstance(notifier, HipChatNotifier)
    assert notifier.config.color == "yellow"


def test_get_notifier_hipchat_with_custom_server():
    from cron_watcher.notifiers.hipchat_notifier import HipChatNotifier

    notifier = get_notifier(
        "hipchat",
        {"token": "tok", "room_id": "99", "server_url": "https://hipchat.example.com"},
    )
    assert isinstance(notifier, HipChatNotifier)
    assert notifier.config.server_url == "https://hipchat.example.com"
