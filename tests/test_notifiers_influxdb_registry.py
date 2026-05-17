import pytest
from unittest.mock import patch, MagicMock

from cron_watcher.notifiers import get_notifier


def _mock_response(status=204):
    resp = MagicMock()
    resp.status = status
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def test_get_notifier_returns_influxdb_notifier():
    from cron_watcher.notifiers.influxdb_notifier import InfluxDBNotifier

    notifier = get_notifier(
        "influxdb",
        url="http://localhost:8086",
        token="tok",
        org="org",
        bucket="bucket",
    )
    assert isinstance(notifier, InfluxDBNotifier)


def test_get_notifier_influxdb_case_insensitive():
    from cron_watcher.notifiers.influxdb_notifier import InfluxDBNotifier

    notifier = get_notifier(
        "InfluxDB",
        url="http://localhost:8086",
        token="tok",
        org="org",
        bucket="bucket",
    )
    assert isinstance(notifier, InfluxDBNotifier)


def test_get_notifier_influxdb_send_returns_true():
    notifier = get_notifier(
        "influxdb",
        url="http://localhost:8086",
        token="tok",
        org="org",
        bucket="bucket",
    )
    with patch("urllib.request.urlopen", return_value=_mock_response(204)):
        result = notifier.send("Test alert", "job missed")
    assert result is True


def test_get_notifier_influxdb_with_custom_measurement():
    from cron_watcher.notifiers.influxdb_notifier import InfluxDBNotifier

    notifier = get_notifier(
        "influxdb",
        url="http://localhost:8086",
        token="tok",
        org="org",
        bucket="bucket",
        measurement="alerts",
    )
    assert isinstance(notifier, InfluxDBNotifier)
    assert notifier._config.measurement == "alerts"


def test_get_notifier_influxdb_with_tags():
    from cron_watcher.notifiers.influxdb_notifier import InfluxDBNotifier

    notifier = get_notifier(
        "influxdb",
        url="http://localhost:8086",
        token="tok",
        org="org",
        bucket="bucket",
        tags={"env": "staging"},
    )
    assert isinstance(notifier, InfluxDBNotifier)
    assert notifier._config.tags == {"env": "staging"}
