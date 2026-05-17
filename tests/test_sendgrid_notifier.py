import json
from unittest.mock import MagicMock, patch
import urllib.error
import pytest

from cron_watcher.notifiers.sendgrid_notifier import SendGridConfig, SendGridNotifier


@pytest.fixture
def sendgrid_config():
    return SendGridConfig(
        api_key="SG.test-key",
        from_email="alerts@example.com",
        to_emails=["ops@example.com", "dev@example.com"],
        subject_prefix="[cron-watcher]",
        timeout=5,
    )


@pytest.fixture
def notifier(sendgrid_config):
    return SendGridNotifier(sendgrid_config)


def _mock_response(status=202):
    resp = MagicMock()
    resp.status = status
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def test_send_returns_true_on_success(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response(202)):
        result = notifier.send("Job missed", "backup-job did not run")
    assert result is True


def test_send_returns_false_on_http_error(notifier):
    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError("connection refused"),
    ):
        result = notifier.send("Job missed", "backup-job did not run")
    assert result is False


def test_send_posts_correct_payload(notifier):
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["headers"] = dict(req.headers)
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _mock_response(202)

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        notifier.send("Failure", "Something went wrong")

    assert captured["url"] == SendGridNotifier.API_URL
    assert "Bearer SG.test-key" in captured["headers"].get("Authorization", "")
    body = captured["body"]
    assert body["from"]["email"] == "alerts@example.com"
    recipients = [r["email"] for r in body["personalizations"][0]["to"]]
    assert "ops@example.com" in recipients
    assert "dev@example.com" in recipients
    assert body["personalizations"][0]["subject"] == "[cron-watcher] Failure"
    assert body["content"][0]["value"] == "Something went wrong"


def test_send_returns_false_on_non_202_status(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response(400)):
        result = notifier.send("Job missed", "details")
    assert result is False


def test_send_uses_subject_prefix(notifier):
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _mock_response(202)

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        notifier.send("Alert", "msg")

    subject = captured["body"]["personalizations"][0]["subject"]
    assert subject.startswith("[cron-watcher]")
