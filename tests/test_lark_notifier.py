import pytest
import requests
from unittest.mock import MagicMock, patch
from cron_watcher.notifiers.lark_notifier import LarkConfig, LarkNotifier


@pytest.fixture
def lark_config():
    return LarkConfig(webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/abc123")


@pytest.fixture
def notifier(lark_config):
    return LarkNotifier(lark_config)


def _mock_response(status_code=200, json_data=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data or {"code": 0, "msg": "success"}
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError()
    else:
        mock.raise_for_status.return_value = None
    return mock


def test_send_returns_true_on_success(notifier):
    with patch("requests.post", return_value=_mock_response()) as mock_post:
        result = notifier.send("Job missed", "nightly_sync did not run")
    assert result is True
    mock_post.assert_called_once()


def test_send_posts_correct_payload(notifier):
    with patch("requests.post", return_value=_mock_response()) as mock_post:
        notifier.send("Alert", "Details")
    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["msg_type"] == "text"
    assert "Alert" in payload["content"]["text"]
    assert "Details" in payload["content"]["text"]


def test_send_returns_false_when_lark_code_nonzero(notifier):
    with patch("requests.post", return_value=_mock_response(json_data={"code": 19001})):
        result = notifier.send("Alert", "body")
    assert result is False


def test_send_returns_false_on_request_error(notifier):
    with patch("requests.post", side_effect=requests.ConnectionError()):
        result = notifier.send("Alert", "body")
    assert result is False


def test_send_returns_false_on_http_error(notifier):
    with patch("requests.post", return_value=_mock_response(status_code=500)):
        result = notifier.send("Alert", "body")
    assert result is False


def test_send_uses_configured_timeout(lark_config):
    lark_config.timeout = 30
    notifier = LarkNotifier(lark_config)
    with patch("requests.post", return_value=_mock_response()) as mock_post:
        notifier.send("x", "y")
    assert mock_post.call_args[1]["timeout"] == 30
