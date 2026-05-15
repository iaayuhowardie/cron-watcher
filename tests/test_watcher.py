"""Tests for the Watcher class."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from cron_watcher.config import AlertConfig, AppConfig, JobConfig
from cron_watcher.scheduler import JobState, Scheduler
from cron_watcher.watcher import Watcher


@pytest.fixture
def job_config():
    return JobConfig(name="backup", schedule="0 * * * *", timeout=300)


@pytest.fixture
def app_config(job_config):
    return AppConfig(
        jobs=[job_config],
        alert=AlertConfig(method="log"),
    )


@pytest.fixture
def mock_scheduler():
    scheduler = MagicMock(spec=Scheduler)
    scheduler.get_state.return_value = JobState(
        last_run=datetime.utcnow() - timedelta(hours=2),
        last_alerted=None,
        last_success=None,
    )
    scheduler.is_missed.return_value = False
    return scheduler


@pytest.fixture
def mock_alerter():
    alerter = MagicMock()
    alerter.send_missed_run_alert.return_value = True
    alerter.send_failure_alert.return_value = True
    return alerter


@pytest.fixture
def watcher(app_config, mock_scheduler, mock_alerter):
    return Watcher(app_config, scheduler=mock_scheduler, alerter=mock_alerter)


def test_check_jobs_no_issues(watcher, mock_scheduler):
    mock_scheduler.is_missed.return_value = False
    issues = watcher.check_jobs()
    assert issues == {}


def test_check_jobs_detects_missed_run(watcher, mock_scheduler, mock_alerter):
    mock_scheduler.is_missed.return_value = True
    issues = watcher.check_jobs()
    assert "backup" in issues
    assert "missed_run" in issues["backup"]
    mock_alerter.send_missed_run_alert.assert_called_once()


def test_check_jobs_marks_alerted_on_success(watcher, mock_scheduler, mock_alerter):
    mock_scheduler.is_missed.return_value = True
    mock_alerter.send_missed_run_alert.return_value = True
    watcher.check_jobs()
    mock_scheduler.mark_alerted.assert_called_once_with("backup")


def test_report_failure_sends_alert(watcher, mock_scheduler, mock_alerter):
    result = watcher.report_failure("backup", exit_code=1, output="error")
    assert result is True
    mock_alerter.send_failure_alert.assert_called_once()
    mock_scheduler.record_run.assert_called_once_with("backup", success=False)


def test_report_failure_unknown_job(watcher):
    result = watcher.report_failure("nonexistent", exit_code=1)
    assert result is False


def test_report_success_records_run(watcher, mock_scheduler):
    watcher.report_success("backup")
    mock_scheduler.record_run.assert_called_once_with("backup", success=True)


def test_stop_sets_running_false(watcher):
    watcher._running = True
    watcher.stop()
    assert watcher._running is False
