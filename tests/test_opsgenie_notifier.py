from unittest.mock import MagicMock, patch

import pytest
import requests

from cron_watcher.notifiers.opsgenie_notifier import OpsGenieConfig, OpsGenieNotifier


@pytest.fixture
def opsgenie_config():
    return OpsGenieConfig(
        api_key="test-api-key",
        team="ops-team",
        priority="P2",
        tags=["cron", "production"],
    )


@pytest.fixture
def notifier(opsgenie_config):
    return OpsGenieNotifier(opsgenie_config)


def _mock_response(status_code=202):
    mock = MagicMock()
    mock.status_code = status_code
    mock.raise_for_status = MagicMock()
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)
    return mock


def test_send_returns_true_on_success(notifier):
    with patch.object(notifier._session, "post", return_value=_mock_response(202)) as mock_post:
        result = notifier.send("Job missed", "backup-job did not run")
    assert result is True
    mock_post.assert_called_once()


def test_send_posts_correct_payload(notifier):
    with patch.object(notifier._session, "post", return_value=_mock_response(202)) as mock_post:
        notifier.send("Job failed", "nightly-sync exited with code 1")

    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["message"] == "Job failed"
    assert payload["description"] == "nightly-sync exited with code 1"
    assert payload["priority"] == "P2"
    assert payload["responders"] == [{"name": "ops-team", "type": "team"}]
    assert payload["tags"] == ["cron", "production"]


def test_send_returns_false_on_request_error(notifier):
    with patch.object(
        notifier._session, "post", side_effect=requests.ConnectionError("timeout")
    ):
        result = notifier.send("Job missed", "backup-job did not run")
    assert result is False


def test_send_returns_false_on_http_error(notifier):
    with patch.object(notifier._session, "post", return_value=_mock_response(403)):
        result = notifier.send("Job missed", "backup-job did not run")
    assert result is False


def test_send_without_team_and_tags():
    config = OpsGenieConfig(api_key="key-only")
    notifier = OpsGenieNotifier(config)
    with patch.object(notifier._session, "post", return_value=_mock_response(202)) as mock_post:
        result = notifier.send("Alert", "Something went wrong")

    assert result is True
    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert "responders" not in payload
    assert "tags" not in payload
    assert payload["priority"] == "P3"
