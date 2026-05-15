"""Tests for cron_watcher.alerter module."""

import smtplib
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from cron_watcher.alerter import Alerter
from cron_watcher.config import AlertConfig, JobConfig


@pytest.fixture
def alert_config() -> AlertConfig:
    return AlertConfig(
        smtp_host="localhost",
        smtp_port=1025,
        smtp_use_tls=False,
        smtp_username=None,
        smtp_password=None,
        from_email="watcher@example.com",
        to_emails=["ops@example.com"],
    )


@pytest.fixture
def sample_job() -> JobConfig:
    return JobConfig(name="backup", schedule="0 2 * * *", grace_period=5)


@pytest.fixture
def alerter(alert_config: AlertConfig) -> Alerter:
    return Alerter(alert_config)


@patch("cron_watcher.alerter.smtplib.SMTP")
def test_send_missed_run_alert_returns_true(mock_smtp, alerter, sample_job):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    expected_at = datetime(2024, 1, 15, 2, 0, 0)
    result = alerter.send_missed_run_alert(sample_job, expected_at)

    assert result is True
    mock_server.sendmail.assert_called_once()


@patch("cron_watcher.alerter.smtplib.SMTP")
def test_send_failure_alert_returns_true(mock_smtp, alerter, sample_job):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    result = alerter.send_failure_alert(sample_job, exit_code=1, output="Error: disk full")

    assert result is True
    _, _, sent_body = mock_server.sendmail.call_args[0]
    assert "Exit code: 1" in sent_body
    assert "Error: disk full" in sent_body


@patch("cron_watcher.alerter.smtplib.SMTP")
def test_send_failure_alert_subject_contains_job_name(mock_smtp, alerter, sample_job):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    alerter.send_failure_alert(sample_job, exit_code=2)

    _, _, sent_message = mock_server.sendmail.call_args[0]
    assert "backup" in sent_message


@patch("cron_watcher.alerter.smtplib.SMTP")
def test_dispatch_returns_false_on_smtp_error(mock_smtp, alerter, sample_job):
    mock_smtp.return_value.__enter__.side_effect = smtplib.SMTPException("connection refused")

    result = alerter.send_missed_run_alert(sample_job, datetime.utcnow())

    assert result is False


@patch("cron_watcher.alerter.smtplib.SMTP")
def test_dispatch_uses_tls_when_configured(mock_smtp, alert_config, sample_job):
    alert_config.smtp_use_tls = True
    alert_config.smtp_username = "user"
    alert_config.smtp_password = "pass"
    alerter = Alerter(alert_config)
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    alerter.send_failure_alert(sample_job, exit_code=1)

    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("user", "pass")
