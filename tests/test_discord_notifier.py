"""Tests for the Discord webhook notifier."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from cron_watcher.notifiers.discord_notifier import DiscordConfig, DiscordNotifier


@pytest.fixture()
def discord_config() -> DiscordConfig:
    return DiscordConfig(
        webhook_url="https://discord.com/api/webhooks/123/abc",
        username="cron-watcher",
        avatar_url="https://example.com/avatar.png",
        timeout=5,
    )


@pytest.fixture()
def notifier(discord_config: DiscordConfig) -> DiscordNotifier:
    return DiscordNotifier(discord_config)


def _mock_response(status_code: int = 204) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)
    else:
        mock.raise_for_status.return_value = None
    return mock


def test_send_returns_true_on_success(notifier: DiscordNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(204)) as mock_post:
        result = notifier.send("Job failed", "backup-db missed its schedule")

    assert result is True
    mock_post.assert_called_once()


def test_send_posts_correct_payload(notifier: DiscordNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(204)) as mock_post:
        notifier.send("Alert title", "Alert body")

    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["username"] == "cron-watcher"
    assert payload["avatar_url"] == "https://example.com/avatar.png"
    assert len(payload["embeds"]) == 1
    embed = payload["embeds"][0]
    assert embed["title"] == "Alert title"
    assert embed["description"] == "Alert body"
    assert embed["color"] == 0xFF0000


def test_send_returns_false_on_request_error(notifier: DiscordNotifier) -> None:
    with patch(
        "requests.post",
        side_effect=requests.ConnectionError("connection refused"),
    ):
        result = notifier.send("Job failed", "details")

    assert result is False


def test_send_returns_false_on_http_error(notifier: DiscordNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(400)):
        result = notifier.send("Job failed", "details")

    assert result is False


def test_send_without_avatar_url() -> None:
    config = DiscordConfig(webhook_url="https://discord.com/api/webhooks/999/xyz")
    notifier = DiscordNotifier(config)

    with patch("requests.post", return_value=_mock_response(204)) as mock_post:
        result = notifier.send("No avatar", "body text")

    assert result is True
    _, kwargs = mock_post.call_args
    assert "avatar_url" not in kwargs["json"]
