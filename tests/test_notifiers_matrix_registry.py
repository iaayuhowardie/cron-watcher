import pytest

from cron_watcher.notifiers import get_notifier


def test_get_notifier_returns_matrix_notifier():
    config = {
        "homeserver_url": "https://matrix.example.com",
        "access_token": "syt_test_token",
        "room_id": "!roomid:example.com",
    }
    notifier = get_notifier("matrix", config)
    assert notifier is not None
    from cron_watcher.notifiers.matrix_notifier import MatrixNotifier
    assert isinstance(notifier, MatrixNotifier)


def test_get_notifier_matrix_case_insensitive():
    config = {
        "homeserver_url": "https://matrix.example.com",
        "access_token": "syt_test_token",
        "room_id": "!roomid:example.com",
    }
    notifier_lower = get_notifier("matrix", config)
    notifier_upper = get_notifier("MATRIX", config)
    notifier_mixed = get_notifier("Matrix", config)
    assert notifier_lower is not None
    assert notifier_upper is not None
    assert notifier_mixed is not None


def test_get_notifier_matrix_send_returns_true(mocker):
    config = {
        "homeserver_url": "https://matrix.example.com",
        "access_token": "syt_test_token",
        "room_id": "!roomid:example.com",
    }
    notifier = get_notifier("matrix", config)
    mock_resp = mocker.MagicMock()
    mock_resp.raise_for_status.return_value = None
    mocker.patch("requests.post", return_value=mock_resp)
    result = notifier.send("Test subject", "Test body")
    assert result is True


def test_get_notifier_matrix_with_custom_timeout():
    config = {
        "homeserver_url": "https://matrix.example.com",
        "access_token": "syt_test_token",
        "room_id": "!roomid:example.com",
        "timeout": 30,
    }
    notifier = get_notifier("matrix", config)
    assert notifier is not None
    assert notifier.config.timeout == 30
