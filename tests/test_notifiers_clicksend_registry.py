from unittest.mock import MagicMock, patch

import pytest
import requests

from cron_watcher.notifiers import get_notifier


def _mock_response(status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)
    else:
        mock.raise_for_status.return_value = None
    return mock


_CLICKSEND_CONF = {
    "username": "user",
    "api_key": "key123",
    "from_number": "+10000000000",
    "to_number": "+19999999999",
}


def test_get_notifier_returns_clicksend_notifier() -> None:
    from cron_watcher.notifiers.clicksend_notifier import ClickSendNotifier

    notifier = get_notifier("clicksend", _CLICKSEND_CONF)
    assert isinstance(notifier, ClickSendNotifier)


def test_get_notifier_clicksend_case_insensitive() -> None:
    from cron_watcher.notifiers.clicksend_notifier import ClickSendNotifier

    notifier = get_notifier("ClickSend", _CLICKSEND_CONF)
    assert isinstance(notifier, ClickSendNotifier)


def test_get_notifier_clicksend_send_returns_true() -> None:
    notifier = get_notifier("clicksend", _CLICKSEND_CONF)
    assert notifier is not None
    with patch("requests.post", return_value=_mock_response(200)):
        result = notifier.send("Test subject", "Test message")
    assert result is True


def test_get_notifier_clicksend_with_custom_timeout() -> None:
    from cron_watcher.notifiers.clicksend_notifier import ClickSendNotifier

    conf = {**_CLICKSEND_CONF, "timeout": 15}
    notifier = get_notifier("clicksend", conf)
    assert isinstance(notifier, ClickSendNotifier)
    assert notifier.config.timeout == 15
