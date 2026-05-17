import json
import urllib.error
from unittest.mock import MagicMock, patch
import pytest
from cron_watcher.notifiers.grafana_notifier import GrafanaConfig, GrafanaNotifier


@pytest.fixture
def grafana_config():
    return GrafanaConfig(
        url="https://grafana.example.com",
        api_key="glsa_test_key",
        tags=["cron", "alert"],
        timeout=5,
    )


@pytest.fixture
def notifier(grafana_config):
    return GrafanaNotifier(grafana_config)


def _mock_response(status=200):
    resp = MagicMock()
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    resp.status = status
    return resp


def test_send_returns_true_on_success(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response()):
        assert notifier.send("Job missed", "backup_daily did not run") is True


def test_send_posts_correct_payload(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response()) as mock_open:
        notifier.send("Job missed", "backup_daily did not run")
        request = mock_open.call_args[0][0]
        body = json.loads(request.data.decode())
        assert "Job missed" in body["text"]
        assert "backup_daily did not run" in body["text"]
        assert body["tags"] == ["cron", "alert"]


def test_send_posts_to_correct_url(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response()) as mock_open:
        notifier.send("subject", "body")
        request = mock_open.call_args[0][0]
        assert request.full_url == "https://grafana.example.com/api/annotations"


def test_send_uses_bearer_auth(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response()) as mock_open:
        notifier.send("subject", "body")
        request = mock_open.call_args[0][0]
        assert request.get_header("Authorization") == "Bearer glsa_test_key"


def test_send_returns_false_on_request_error(notifier):
    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError("connection refused"),
    ):
        assert notifier.send("subject", "body") is False


def test_send_with_empty_tags():
    cfg = GrafanaConfig(
        url="https://grafana.example.com",
        api_key="key",
        tags=[],
    )
    n = GrafanaNotifier(cfg)
    with patch("urllib.request.urlopen", return_value=_mock_response()) as mock_open:
        result = n.send("subject", "body")
        body = json.loads(mock_open.call_args[0][0].data.decode())
        assert result is True
        assert body["tags"] == []
