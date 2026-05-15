"""Main watcher daemon that ties together scheduler, alerter, and log parsing."""

import logging
import time
from datetime import datetime
from typing import Optional

from cron_watcher.alerter import Alerter
from cron_watcher.config import AppConfig, JobConfig
from cron_watcher.scheduler import JobState, Scheduler

logger = logging.getLogger(__name__)


class Watcher:
    """Monitors cron jobs and triggers alerts on missed runs or failures."""

    def __init__(self, config: AppConfig, scheduler: Optional[Scheduler] = None, alerter: Optional[Alerter] = None):
        self.config = config
        self.scheduler = scheduler or Scheduler(config.jobs)
        self.alerter = alerter or Alerter(config.alert)
        self._running = False

    def check_jobs(self) -> dict[str, list[str]]:
        """Check all jobs for missed runs. Returns a dict of job name -> list of issues."""
        issues: dict[str, list[str]] = {}
        now = datetime.utcnow()

        for job in self.config.jobs:
            state: JobState = self.scheduler.get_state(job.name)
            job_issues = []

            if self.scheduler.is_missed(job, state, now):
                logger.warning("Missed run detected for job: %s", job.name)
                sent = self.alerter.send_missed_run_alert(job, state.last_run)
                if sent:
                    self.scheduler.mark_alerted(job.name)
                job_issues.append("missed_run")

            if job_issues:
                issues[job.name] = job_issues

        return issues

    def report_failure(self, job_name: str, exit_code: int, output: str = "") -> bool:
        """Report a job failure. Returns True if alert was sent."""
        job = self._find_job(job_name)
        if job is None:
            logger.error("Unknown job reported failure: %s", job_name)
            return False

        self.scheduler.record_run(job_name, success=False)
        sent = self.alerter.send_failure_alert(job, exit_code, output)
        logger.info("Failure alert sent for %s: %s", job_name, sent)
        return sent

    def report_success(self, job_name: str) -> None:
        """Record a successful job run."""
        self.scheduler.record_run(job_name, success=True)
        logger.debug("Recorded success for job: %s", job_name)

    def run(self, poll_interval: int = 60) -> None:
        """Start the watcher loop."""
        self._running = True
        logger.info("Watcher started, polling every %d seconds", poll_interval)
        while self._running:
            self.check_jobs()
            time.sleep(poll_interval)

    def stop(self) -> None:
        """Stop the watcher loop."""
        self._running = False
        logger.info("Watcher stopped")

    def _find_job(self, job_name: str) -> Optional[JobConfig]:
        return next((j for j in self.config.jobs if j.name == job_name), None)
