import pytest
import requests

from cron_watcher.notifiers.newrelic_notifier import NewRelicConfig, NewRelicNotifier


@pytest.fixture
def newrelic_config() -> NewRelicConfig:
    return NewRelicConfig(
        account_id="123456",
        insert_key="test-insert-key",
        event_type="CronWatcherAlert",
        timeout=5,
    )


@pytest.fixture
def notifier(newrelic_config: NewRelicConfig) -> NewRelicNotifier:
    return NewRelicNotifier(config=newrelic_config)


def _mock_response(mocker, status_code: int = 200, raise_exc=None):
    mock_resp = mocker.MagicMock()
    mock_resp.status_code = status_code
    if raise_exc:
        mock_resp.raise_for_status.side_effect = raise_exc
    else:
        mock_resp.raise_for_status.return_value = None
    return mock_resp


def test_send_returns_true_on_success(mocker, notifier):
    mock_post = mocker.patch("requests.post", return_value=_mock_response(mocker, 200))
    result = notifier.send("Test Subject", "Test body")
    assert result is True
    mock_post.assert_called_once()


def test_send_posts_correct_payload(mocker, notifier):
    mock_post = mocker.patch("requests.post", return_value=_mock_response(mocker, 200))
    notifier.send("Job missed", "backup-job did not run")
    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["eventType"] == "CronWatcherAlert"
    assert payload["subject"] == "Job missed"
    assert payload["message"] == "backup-job did not run"


def test_send_uses_correct_url(mocker, notifier):
    mock_post = mocker.patch("requests.post", return_value=_mock_response(mocker, 200))
    notifier.send("subject", "body")
    url = mock_post.call_args[0][0]
    assert "123456" in url
    assert "insights-collector.newrelic.com" in url


def test_send_returns_false_on_request_error(mocker, notifier):
    mocker.patch(
        "requests.post",
        side_effect=requests.RequestException("connection refused"),
    )
    result = notifier.send("subject", "body")
    assert result is False


def test_send_returns_false_on_http_error(mocker, notifier):
    mock_post = mocker.patch(
        "requests.post",
        return_value=_mock_response(
            mocker, 403, raise_exc=requests.HTTPError("403 Forbidden")
        ),
    )
    result = notifier.send("subject", "body")
    assert result is False


def test_send_includes_insert_key_header(mocker, notifier):
    mock_post = mocker.patch("requests.post", return_value=_mock_response(mocker, 200))
    notifier.send("subject", "body")
    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["X-Insert-Key"] == "test-insert-key"
