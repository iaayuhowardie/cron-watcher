"""Tests for the ntfy notifier."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from cron_watcher.notifiers.ntfy_notifier import NtfyConfig, NtfyNotifier


@pytest.fixture
def ntfy_config() -> NtfyConfig:
    return NtfyConfig(
        topic="cron-alerts",
        server="https://ntfy.sh",
        priority="high",
        tags="warning,cron",
    )


@pytest.fixture
def notifier(ntfy_config: NtfyConfig) -> NtfyNotifier:
    return NtfyNotifier(ntfy_config)


def _mock_response(status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)
    else:
        mock.raise_for_status.return_value = None
    return mock


def test_send_returns_true_on_success(notifier: NtfyNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        result = notifier.send("Job failed", "backup-db missed its run")
    assert result is True
    mock_post.assert_called_once()


def test_send_posts_to_correct_url(notifier: NtfyNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Subject", "Body")
    call_url = mock_post.call_args[0][0]
    assert call_url == "https://ntfy.sh/cron-alerts"


def test_send_includes_title_and_priority_headers(notifier: NtfyNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Alert Title", "Alert body")
    headers = mock_post.call_args[1]["headers"]
    assert headers["Title"] == "Alert Title"
    assert headers["Priority"] == "high"


def test_send_includes_tags_header(notifier: NtfyNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Subject", "Body")
    headers = mock_post.call_args[1]["headers"]
    assert headers["Tags"] == "warning,cron"


def test_send_omits_tags_header_when_not_set() -> None:
    config = NtfyConfig(topic="alerts")
    notifier = NtfyNotifier(config)
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Subject", "Body")
    headers = mock_post.call_args[1]["headers"]
    assert "Tags" not in headers


def test_send_includes_auth_header_when_token_set() -> None:
    config = NtfyConfig(topic="private", token="tk_secret123")
    notifier = NtfyNotifier(config)
    with patch("requests.post", return_value=_mock_response(200)) as mock_post:
        notifier.send("Subject", "Body")
    headers = mock_post.call_args[1]["headers"]
    assert headers["Authorization"] == "Bearer tk_secret123"


def test_send_returns_false_on_request_error(notifier: NtfyNotifier) -> None:
    with patch("requests.post", side_effect=requests.ConnectionError()):
        result = notifier.send("Subject", "Body")
    assert result is False


def test_send_returns_false_on_http_error(notifier: NtfyNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(403)):
        result = notifier.send("Subject", "Body")
    assert result is False
