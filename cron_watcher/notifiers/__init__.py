"""Notifier backends for cron-watcher."""

from cron_watcher.notifiers.email_notifier import EmailConfig, EmailNotifier

__all__ = ["EmailConfig", "EmailNotifier"]
