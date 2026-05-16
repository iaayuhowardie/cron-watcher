"""Tests for the notifier registry (get_notifier)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from cron_watcher.notifiers import get_notifier


def test_get_notifier_returns_none_for_unknown_type() -> None:
    result = get_notifier("carrier_pigeon", {})
    assert result is None


def test_get_notifier_is_case_insensitive() -> None:
    result = get_notifier("carrier_pigeon", {})
    assert result is None  # unknown but no crash


def test_get_notifier_returns_log_notifier() -> None:
    notifier = get_notifier("log", {"name": "cron-watcher"})
    assert notifier is not None
    assert hasattr(notifier, "send")


def test_get_notifier_log_notifier_send_returns_true() -> None:
    notifier = get_notifier("log", {"name": "cron-watcher"})
    assert notifier is not None
    result = notifier.send("Test subject", "Test body")
    assert result is True


def test_get_notifier_returns_slack_notifier() -> None:
    notifier = get_notifier("slack", {"webhook_url": "https://hooks.slack.com/test"})
    assert notifier is not None
    assert hasattr(notifier, "send")


def test_get_notifier_returns_ntfy_notifier() -> None:
    notifier = get_notifier("ntfy", {"topic": "alerts"})
    assert notifier is not None
    assert hasattr(notifier, "send")


def test_get_notifier_ntfy_case_insensitive() -> None:
    notifier = get_notifier("NTFY", {"topic": "alerts"})
    assert notifier is not None


def test_get_notifier_ntfy_send_delegates_to_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    import requests

    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None

    with patch("requests.post", return_value=mock_resp) as mock_post:
        notifier = get_notifier("ntfy", {"topic": "cron-alerts"})
        assert notifier is not None
        result = notifier.send("Job missed", "backup-db missed its scheduled run")

    assert result is True
    mock_post.assert_called_once()
