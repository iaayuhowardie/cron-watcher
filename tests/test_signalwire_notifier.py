import pytest
from unittest.mock import MagicMock, patch
from cron_watcher.notifiers.signalwire_notifier import SignalWireConfig, SignalWireNotifier


@pytest.fixture
def signalwire_config():
    return SignalWireConfig(
        project_id="test-project-id",
        api_token="test-api-token",
        space_url="example.signalwire.com",
        from_number="+15550000001",
        to_number="+15550000002",
        timeout=5,
    )


@pytest.fixture
def notifier(signalwire_config):
    return SignalWireNotifier(signalwire_config)


def _mock_response(status_code=201, json_data=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data or {"sid": "SM123456"}
    if status_code >= 400:
        mock.raise_for_status.side_effect = __import__(
            "requests"
        ).HTTPError(response=mock)
    else:
        mock.raise_for_status.return_value = None
    return mock


@patch("cron_watcher.notifiers.signalwire_notifier.requests")
def test_send_returns_true_on_success(mock_requests, notifier):
    mock_requests.post.return_value = _mock_response(201)
    mock_requests.RequestException = __import__("requests").RequestException
    result = notifier.send("Job missed", "backup-job did not run")
    assert result is True


@patch("cron_watcher.notifiers.signalwire_notifier.requests")
def test_send_posts_correct_payload(mock_requests, notifier, signalwire_config):
    mock_requests.post.return_value = _mock_response(201)
    mock_requests.RequestException = __import__("requests").RequestException
    notifier.send("Alert", "details here")
    _, kwargs = mock_requests.post.call_args
    assert kwargs["data"]["From"] == signalwire_config.from_number
    assert kwargs["data"]["To"] == signalwire_config.to_number
    assert "Alert" in kwargs["data"]["Body"]
    assert "details here" in kwargs["data"]["Body"]


@patch("cron_watcher.notifiers.signalwire_notifier.requests")
def test_send_uses_correct_auth(mock_requests, notifier, signalwire_config):
    mock_requests.post.return_value = _mock_response(201)
    mock_requests.RequestException = __import__("requests").RequestException
    notifier.send("Alert", "body")
    _, kwargs = mock_requests.post.call_args
    assert kwargs["auth"] == (
        signalwire_config.project_id,
        signalwire_config.api_token,
    )


@patch("cron_watcher.notifiers.signalwire_notifier.requests")
def test_send_returns_false_on_http_error(mock_requests, notifier):
    import requests as req
    mock_requests.post.return_value = _mock_response(400)
    mock_requests.RequestException = req.RequestException
    result = notifier.send("Alert", "body")
    assert result is False


@patch("cron_watcher.notifiers.signalwire_notifier.requests")
def test_send_returns_false_on_connection_error(mock_requests, notifier):
    import requests as req
    mock_requests.post.side_effect = req.ConnectionError("unreachable")
    mock_requests.RequestException = req.RequestException
    result = notifier.send("Alert", "body")
    assert result is False


@patch("cron_watcher.notifiers.signalwire_notifier.requests")
def test_send_uses_space_url_in_endpoint(mock_requests, notifier, signalwire_config):
    mock_requests.post.return_value = _mock_response(201)
    mock_requests.RequestException = __import__("requests").RequestException
    notifier.send("Alert", "body")
    call_url = mock_requests.post.call_args[0][0]
    assert signalwire_config.space_url in call_url
    assert signalwire_config.project_id in call_url
