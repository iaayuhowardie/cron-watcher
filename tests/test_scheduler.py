"""Tests for the Scheduler and JobState classes."""

from datetime import datetime, timezone

import pytest

from cron_watcher.config import JobConfig
from cron_watcher.scheduler import JobState, Scheduler


@pytest.fixture()
def every_minute_job() -> JobConfig:
    return JobConfig(name="heartbeat", schedule="* * * * *", timeout=30)


@pytest.fixture()
def hourly_job() -> JobConfig:
    return JobConfig(name="hourly-report", schedule="0 * * * *", timeout=120)


@pytest.fixture()
def scheduler(every_minute_job, hourly_job) -> Scheduler:
    return Scheduler(jobs=[every_minute_job, hourly_job])


class TestJobState:
    def test_expected_last_run_is_in_the_past(self, every_minute_job):
        now = datetime(2024, 6, 1, 12, 5, 30, tzinfo=timezone.utc)
        state = JobState(every_minute_job)
        expected = state.expected_last_run(now)
        assert expected < now

    def test_is_missed_when_no_success_recorded(self, every_minute_job):
        state = JobState(every_minute_job)
        now = datetime(2024, 6, 1, 12, 5, 0, tzinfo=timezone.utc)
        assert state.is_missed(now) is True

    def test_is_not_missed_after_recent_success(self, every_minute_job):
        state = JobState(every_minute_job)
        now = datetime(2024, 6, 1, 12, 5, 30, tzinfo=timezone.utc)
        # last success was at :05 which equals expected last run at :05
        state.last_success = datetime(2024, 6, 1, 12, 5, 0, tzinfo=timezone.utc)
        assert state.is_missed(now) is False

    def test_is_missed_when_success_is_stale(self, every_minute_job):
        state = JobState(every_minute_job)
        now = datetime(2024, 6, 1, 12, 7, 30, tzinfo=timezone.utc)
        state.last_success = datetime(2024, 6, 1, 12, 5, 0, tzinfo=timezone.utc)
        assert state.is_missed(now) is True


class TestScheduler:
    def test_initial_states_created_for_all_jobs(self, scheduler):
        assert "heartbeat" in scheduler.states
        assert "hourly-report" in scheduler.states

    def test_record_success_updates_last_success(self, scheduler):
        ts = datetime(2024, 6, 1, 12, 5, 0, tzinfo=timezone.utc)
        scheduler.record_success("heartbeat", at=ts)
        assert scheduler.states["heartbeat"].last_success == ts

    def test_record_success_resets_missed_count(self, scheduler):
        scheduler.states["heartbeat"].missed_count = 3
        scheduler.record_success("heartbeat")
        assert scheduler.states["heartbeat"].missed_count == 0

    def test_record_success_raises_for_unknown_job(self, scheduler):
        with pytest.raises(KeyError, match="unknown-job"):
            scheduler.record_success("unknown-job")

    def test_check_missed_returns_missed_jobs(self, scheduler):
        now = datetime(2024, 6, 1, 12, 5, 30, tzinfo=timezone.utc)
        missed = scheduler.check_missed(now)
        assert "heartbeat" in missed
        assert "hourly-report" in missed

    def test_check_missed_increments_missed_count(self, scheduler):
        now = datetime(2024, 6, 1, 12, 5, 30, tzinfo=timezone.utc)
        scheduler.check_missed(now)
        assert scheduler.states["heartbeat"].missed_count == 1

    def test_check_missed_excludes_successful_jobs(self, scheduler):
        now = datetime(2024, 6, 1, 12, 5, 30, tzinfo=timezone.utc)
        scheduler.record_success(
            "heartbeat",
            at=datetime(2024, 6, 1, 12, 5, 0, tzinfo=timezone.utc),
        )
        missed = scheduler.check_missed(now)
        assert "heartbeat" not in missed
