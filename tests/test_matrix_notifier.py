import pytest
import requests

from cron_watcher.notifiers.matrix_notifier import MatrixConfig, MatrixNotifier


@pytest.fixture
def matrix_config() -> MatrixConfig:
    return MatrixConfig(
        homeserver_url="https://matrix.example.com",
        access_token="syt_test_token",
        room_id="!roomid:example.com",
    )


@pytest.fixture
def notifier(matrix_config: MatrixConfig) -> MatrixNotifier:
    return MatrixNotifier(matrix_config)


def _mock_response(mocker, status_code: int = 200, raise_exc=None):
    mock_resp = mocker.MagicMock()
    mock_resp.status_code = status_code
    if raise_exc:
        mock_resp.raise_for_status.side_effect = raise_exc
    else:
        mock_resp.raise_for_status.return_value = None
    return mocker.patch("requests.post", return_value=mock_resp)


def test_send_returns_true_on_success(notifier, mocker):
    _mock_response(mocker)
    assert notifier.send("Test subject", "Test body") is True


def test_send_posts_correct_payload(notifier, matrix_config, mocker):
    mock_post = _mock_response(mocker)
    notifier.send("Alert", "Job failed")
    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["msgtype"] == "m.text"
    assert "Alert" in payload["body"]
    assert "Job failed" in payload["body"]


def test_send_uses_correct_url(notifier, matrix_config, mocker):
    mock_post = _mock_response(mocker)
    notifier.send("Subject", "Body")
    url = mock_post.call_args[0][0]
    assert matrix_config.homeserver_url in url
    assert matrix_config.room_id in url
    assert "m.room.message" in url


def test_send_includes_bearer_token(notifier, matrix_config, mocker):
    mock_post = _mock_response(mocker)
    notifier.send("Subject", "Body")
    _, kwargs = mock_post.call_args
    auth_header = kwargs["headers"]["Authorization"]
    assert auth_header == f"Bearer {matrix_config.access_token}"


def test_send_returns_false_on_request_error(notifier, mocker):
    _mock_response(
        mocker,
        status_code=403,
        raise_exc=requests.RequestException("Forbidden"),
    )
    assert notifier.send("Subject", "Body") is False


def test_send_returns_false_on_http_error(notifier, mocker):
    _mock_response(
        mocker,
        status_code=500,
        raise_exc=requests.HTTPError("Internal Server Error"),
    )
    assert notifier.send("Subject", "Body") is False


def test_homeserver_url_trailing_slash_stripped(matrix_config, mocker):
    matrix_config.homeserver_url = "https://matrix.example.com/"
    notifier = MatrixNotifier(matrix_config)
    mock_post = _mock_response(mocker)
    notifier.send("Subject", "Body")
    url = mock_post.call_args[0][0]
    assert "//" not in url.replace("https://", "")
