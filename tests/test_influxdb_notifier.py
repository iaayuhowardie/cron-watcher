import pytest
from unittest.mock import patch, MagicMock
import urllib.error

from cron_watcher.notifiers.influxdb_notifier import InfluxDBConfig, InfluxDBNotifier


@pytest.fixture
def influxdb_config():
    return InfluxDBConfig(
        url="http://localhost:8086",
        token="my-token",
        org="my-org",
        bucket="my-bucket",
    )


@pytest.fixture
def notifier(influxdb_config):
    return InfluxDBNotifier(influxdb_config)


def _mock_response(status=204):
    resp = MagicMock()
    resp.status = status
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def test_send_returns_true_on_success(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response(204)):
        result = notifier.send("Job missed", "backup did not run")
    assert result is True


def test_send_returns_true_on_200(notifier):
    with patch("urllib.request.urlopen", return_value=_mock_response(200)):
        result = notifier.send("Job failed", "exit code 1")
    assert result is True


def test_send_returns_false_on_request_error(notifier):
    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError("connection refused"),
    ):
        result = notifier.send("Job missed", "backup did not run")
    assert result is False


def test_send_posts_to_correct_url(influxdb_config):
    notifier = InfluxDBNotifier(influxdb_config)
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["headers"] = dict(req.headers)
        captured["data"] = req.data.decode()
        return _mock_response(204)

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        notifier.send("test subject", "test message")

    assert "org=my-org" in captured["url"]
    assert "bucket=my-bucket" in captured["url"]
    assert "precision=ns" in captured["url"]
    assert "Token my-token" in captured["headers"].get("Authorization", "")


def test_send_line_protocol_format(influxdb_config):
    notifier = InfluxDBNotifier(influxdb_config)
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["data"] = req.data.decode()
        return _mock_response(204)

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        notifier.send("my subject", "my message")

    assert 'subject="my subject"' in captured["data"]
    assert 'message="my message"' in captured["data"]
    assert captured["data"].startswith("cron_watcher ")


def test_send_with_tags(influxdb_config):
    influxdb_config.tags = {"env": "prod", "host": "worker1"}
    notifier = InfluxDBNotifier(influxdb_config)
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["data"] = req.data.decode()
        return _mock_response(204)

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        notifier.send("subject", "message")

    assert "env=prod" in captured["data"]
    assert "host=worker1" in captured["data"]
