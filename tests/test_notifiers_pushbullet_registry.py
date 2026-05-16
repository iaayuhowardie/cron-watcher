import pytest

from cron_watcher.notifiers import get_notifier
from cron_watcher.notifiers.pushbullet_notifier import PushbulletNotifier


def test_get_notifier_returns_pushbullet_notifier() -> None:
    config = {"access_token": "test-token"}
    notifier = get_notifier("pushbullet", config)
    assert isinstance(notifier, PushbulletNotifier)


def test_get_notifier_pushbullet_case_insensitive() -> None:
    config = {"access_token": "test-token"}
    notifier = get_notifier("Pushbullet", config)
    assert isinstance(notifier, PushbulletNotifier)


def test_get_notifier_pushbullet_send_returns_true() -> None:
    from unittest.mock import MagicMock, patch

    config = {"access_token": "test-token"}
    notifier = get_notifier("pushbullet", config)
    assert notifier is not None

    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    with patch("requests.post", return_value=mock_resp):
        result = notifier.send("subject", "body")
    assert result is True


def test_get_notifier_pushbullet_with_device_iden() -> None:
    config = {"access_token": "token", "device_iden": "dev123"}
    notifier = get_notifier("pushbullet", config)
    assert isinstance(notifier, PushbulletNotifier)
    assert notifier.config.device_iden == "dev123"


def test_get_notifier_pushbullet_with_channel_tag() -> None:
    config = {"access_token": "token", "channel_tag": "my-channel"}
    notifier = get_notifier("pushbullet", config)
    assert isinstance(notifier, PushbulletNotifier)
    assert notifier.config.channel_tag == "my-channel"
