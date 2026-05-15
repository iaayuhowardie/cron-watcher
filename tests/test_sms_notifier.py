"""Tests for SMSNotifier."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from cron_watcher.notifiers.sms_notifier import SMSConfig, SMSNotifier


@pytest.fixture
def sms_config() -> SMSConfig:
    return SMSConfig(
        account_sid="ACtest123",
        auth_token="secret",
        from_number="+10000000000",
        to_number="+19999999999",
    )


@pytest.fixture
def notifier(sms_config: SMSConfig) -> SMSNotifier:
    return SMSNotifier(sms_config)


def _mock_response(status_code: int = 201) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    if status_code >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError(response=resp)
    else:
        resp.raise_for_status.return_value = None
    return resp


def test_send_returns_true_on_success(notifier: SMSNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(201)):
        assert notifier.send("Alert", "Job failed") is True


def test_send_returns_false_on_http_error(notifier: SMSNotifier) -> None:
    with patch("requests.post", return_value=_mock_response(401)):
        assert notifier.send("Alert", "Job failed") is False


def test_send_returns_false_on_request_error(notifier: SMSNotifier) -> None:
    with patch("requests.post", side_effect=requests.ConnectionError):
        assert notifier.send("Alert", "Job failed") is False


def test_send_posts_correct_payload(notifier: SMSNotifier, sms_config: SMSConfig) -> None:
    with patch("requests.post", return_value=_mock_response(201)) as mock_post:
        notifier.send("Subject", "Body text")
        _, kwargs = mock_post.call_args
        data = kwargs["data"]
        assert data["From"] == sms_config.from_number
        assert data["To"] == sms_config.to_number
        assert "Subject" in data["Body"]
        assert "Body text" in data["Body"]


def test_send_truncates_long_body(notifier: SMSNotifier) -> None:
    long_body = "x" * 2000
    with patch("requests.post", return_value=_mock_response(201)) as mock_post:
        notifier.send("S", long_body)
        data = mock_post.call_args[1]["data"]
        assert len(data["Body"]) <= 1600


def test_send_uses_correct_auth(notifier: SMSNotifier, sms_config: SMSConfig) -> None:
    with patch("requests.post", return_value=_mock_response(201)) as mock_post:
        notifier.send("Alert", "msg")
        _, kwargs = mock_post.call_args
        assert kwargs["auth"] == (sms_config.account_sid, sms_config.auth_token)
