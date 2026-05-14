"""Scheduler module for tracking cron job execution and detecting missed runs."""

import logging
from datetime import datetime, timezone
from typing import Dict, Optional

from croniter import croniter

from cron_watcher.config import JobConfig

logger = logging.getLogger(__name__)


class JobState:
    """Tracks the runtime state of a monitored cron job."""

    def __init__(self, job: JobConfig) -> None:
        self.job = job
        self.last_success: Optional[datetime] = None
        self.last_checked: Optional[datetime] = None
        self.missed_count: int = 0

    def expected_last_run(self, now: Optional[datetime] = None) -> datetime:
        """Return the most recent expected run time before now."""
        if now is None:
            now = datetime.now(timezone.utc)
        cron = croniter(self.job.schedule, now)
        return cron.get_prev(datetime)

    def is_missed(self, now: Optional[datetime] = None) -> bool:
        """Return True if the job missed its most recent expected run."""
        if now is None:
            now = datetime.now(timezone.utc)
        expected = self.expected_last_run(now)
        if self.last_success is None:
            return True
        return self.last_success < expected


class Scheduler:
    """Manages job states and detects missed cron executions."""

    def __init__(self, jobs: list[JobConfig]) -> None:
        self.states: Dict[str, JobState] = {
            job.name: JobState(job) for job in jobs
        }

    def record_success(self, job_name: str, at: Optional[datetime] = None) -> None:
        """Record a successful execution for the given job."""
        if job_name not in self.states:
            raise KeyError(f"Unknown job: {job_name}")
        ts = at or datetime.now(timezone.utc)
        state = self.states[job_name]
        state.last_success = ts
        state.missed_count = 0
        logger.info("Job '%s' recorded success at %s", job_name, ts.isoformat())

    def check_missed(self, now: Optional[datetime] = None) -> list[str]:
        """Return names of jobs that have missed their last expected run."""
        if now is None:
            now = datetime.now(timezone.utc)
        missed = []
        for name, state in self.states.items():
            state.last_checked = now
            if state.is_missed(now):
                state.missed_count += 1
                logger.warning(
                    "Job '%s' missed its scheduled run (missed_count=%d)",
                    name,
                    state.missed_count,
                )
                missed.append(name)
        return missed
