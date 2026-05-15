"""Tests for the Microsoft Teams notifier."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from cron_watcher.notifiers.teams_notifier import TeamsConfig, TeamsNotifier


@pytest.fixture
def teams_config() -> TeamsConfig:
    return TeamsConfig(
        webhook_url="https://outlook.office.com/webhook/test/IncomingWebhook/abc/123",
        timeout=5,
        theme_color="FF0000",
    )


@pytest.fixture
def notifier(teams_config: TeamsConfig) -> TeamsNotifier:
    return TeamsNotifier(teams_config)


def _mock_response(status_code: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    if status_code >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError(response=resp)
    else:
        resp.raise_for_status.return_value = None
    return resp


def test_send_returns_true_on_success(notifier: TeamsNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        result = notifier.send("Job failed", "backup-db missed its scheduled run")

    assert result is True
    mock_post.assert_called_once()


def test_send_posts_correct_payload(notifier: TeamsNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Alert title", "Alert body text")

    _, kwargs = mock_post.call_args
    payload = kwargs["json"]

    assert payload["@type"] == "MessageCard"
    assert payload["summary"] == "Alert title"
    assert payload["themeColor"] == "FF0000"
    section = payload["sections"][0]
    assert section["activityTitle"] == "Alert title"
    assert section["activityText"] == "Alert body text"


def test_send_uses_configured_timeout(notifier: TeamsNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("x", "y")

    _, kwargs = mock_post.call_args
    assert kwargs["timeout"] == 5


def test_send_returns_false_on_request_error(notifier: TeamsNotifier) -> None:
    with patch(
        "requests.post", side_effect=requests.ConnectionError("unreachable")
    ):
        result = notifier.send("Job failed", "details")

    assert result is False


def test_send_returns_false_on_http_error(notifier: TeamsNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(400)):
        result = notifier.send("Job failed", "details")

    assert result is False


def test_custom_theme_color() -> None:
    config = TeamsConfig(
        webhook_url="https://outlook.office.com/webhook/x",
        theme_color="00FF00",
    )
    n = TeamsNotifier(config)
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        n.send("ok", "all good")

    payload = mock_post.call_args[1]["json"]
    assert payload["themeColor"] == "00FF00"
