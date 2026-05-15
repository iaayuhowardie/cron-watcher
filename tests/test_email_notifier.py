"""Tests for the email notifier."""

import smtplib
from unittest.mock import MagicMock, patch

import pytest

from cron_watcher.notifiers.email_notifier import EmailConfig, EmailNotifier


@pytest.fixture
def email_config() -> EmailConfig:
    return EmailConfig(
        smtp_host="smtp.example.com",
        smtp_port=587,
        sender="alerts@example.com",
        recipients=["ops@example.com", "admin@example.com"],
        username="alerts@example.com",
        password="secret",
        use_tls=True,
    )


@pytest.fixture
def notifier(email_config: EmailConfig) -> EmailNotifier:
    return EmailNotifier(email_config)


def test_send_returns_true_on_success(notifier: EmailNotifier) -> None:
    with patch("smtplib.SMTP") as mock_smtp:
        instance = mock_smtp.return_value.__enter__.return_value
        result = notifier.send("Test subject", "Test body")
    assert result is True
    instance.starttls.assert_called_once()
    instance.login.assert_called_once_with("alerts@example.com", "secret")
    instance.sendmail.assert_called_once()


def test_send_returns_false_on_smtp_error(notifier: EmailNotifier) -> None:
    with patch("smtplib.SMTP") as mock_smtp:
        mock_smtp.return_value.__enter__.side_effect = smtplib.SMTPException("conn error")
        result = notifier.send("Test subject", "Test body")
    assert result is False


def test_send_without_auth() -> None:
    config = EmailConfig(
        smtp_host="localhost",
        smtp_port=25,
        sender="noreply@local",
        recipients=["dev@local"],
        use_tls=False,
    )
    notifier = EmailNotifier(config)
    with patch("smtplib.SMTP") as mock_smtp:
        instance = mock_smtp.return_value.__enter__.return_value
        result = notifier.send("No auth", "body")
    assert result is True
    instance.starttls.assert_not_called()
    instance.login.assert_not_called()


def test_send_includes_all_recipients(notifier: EmailNotifier) -> None:
    with patch("smtplib.SMTP") as mock_smtp:
        instance = mock_smtp.return_value.__enter__.return_value
        notifier.send("Alert", "Something failed")
    _, call_kwargs = instance.sendmail.call_args
    args = instance.sendmail.call_args[0]
    assert args[1] == ["ops@example.com", "admin@example.com"]


def test_email_config_defaults() -> None:
    config = EmailConfig(
        smtp_host="smtp.example.com",
        smtp_port=465,
        sender="a@b.com",
        recipients=["x@y.com"],
    )
    assert config.username is None
    assert config.password is None
    assert config.use_tls is True
