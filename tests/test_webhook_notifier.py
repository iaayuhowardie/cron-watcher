import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from cron_watcher.notifiers.webhook_notifier import WebhookConfig, WebhookNotifier


@pytest.fixture
def webhook_config() -> WebhookConfig:
    return WebhookConfig(url="https://example.com/hook", secret="s3cr3t", timeout=5)


@pytest.fixture
def notifier(webhook_config: WebhookConfig) -> WebhookNotifier:
    return WebhookNotifier(webhook_config)


def _mock_response(status: int = 200):
    mock_resp = MagicMock()
    mock_resp.status = status
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


def test_send_returns_true_on_success(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response(200)):
        result = notifier.send("Test subject", "Test body")
    assert result is True


def test_send_returns_false_on_http_error(notifier):
    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.HTTPError(
            url=None, code=500, msg="Server Error", hdrs=None, fp=None
        ),
    ):
        result = notifier.send("Test subject", "Test body")
    assert result is False


def test_send_returns_false_on_url_error(notifier):
    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError("connection refused"),
    ):
        result = notifier.send("Test subject", "Test body")
    assert result is False


def test_send_posts_correct_payload(notifier):
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["data"] = json.loads(req.data.decode())
        captured["headers"] = dict(req.headers)
        return _mock_response(200)

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        notifier.send("Alert!", "Job failed.")

    assert captured["data"] == {"subject": "Alert!", "body": "Job failed."}
    assert captured["headers"].get("X-webhook-secret") == "s3cr3t"


def test_send_without_secret_omits_header():
    cfg = WebhookConfig(url="https://example.com/hook")
    n = WebhookNotifier(cfg)
    captured_headers = {}

    def fake_urlopen(req, timeout=None):
        captured_headers.update(req.headers)
        return _mock_response(200)

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        result = n.send("subject", "body")

    assert result is True
    assert "X-webhook-secret" not in captured_headers
