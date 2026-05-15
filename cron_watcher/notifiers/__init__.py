from typing import Any, Dict


def get_notifier(notifier_type: str, config: Dict[str, Any]):
    """Factory that returns an instantiated notifier for the given type."""
    if notifier_type == "email":
        from cron_watcher.notifiers.email_notifier import EmailConfig, EmailNotifier
        return EmailNotifier(EmailConfig(**config))

    if notifier_type == "slack":
        from cron_watcher.notifiers.slack_notifier import SlackConfig, SlackNotifier
        return SlackNotifier(SlackConfig(**config))

    if notifier_type == "webhook":
        from cron_watcher.notifiers.webhook_notifier import WebhookConfig, WebhookNotifier
        return WebhookNotifier(WebhookConfig(**config))

    if notifier_type == "pagerduty":
        from cron_watcher.notifiers.pagerduty_notifier import PagerDutyConfig, PagerDutyNotifier
        return PagerDutyNotifier(PagerDutyConfig(**config))

    if notifier_type == "opsgenie":
        from cron_watcher.notifiers.opsgenie_notifier import OpsGenieConfig, OpsGenieNotifier
        return OpsGenieNotifier(OpsGenieConfig(**config))

    if notifier_type == "log":
        from cron_watcher.notifiers.log_notifier import LogConfig, LogNotifier
        return LogNotifier(LogConfig(**config))

    if notifier_type == "teams":
        from cron_watcher.notifiers.teams_notifier import TeamsConfig, TeamsNotifier
        return TeamsNotifier(TeamsConfig(**config))

    if notifier_type == "discord":
        from cron_watcher.notifiers.discord_notifier import DiscordConfig, DiscordNotifier
        return DiscordNotifier(DiscordConfig(**config))

    if notifier_type == "telegram":
        from cron_watcher.notifiers.telegram_notifier import TelegramConfig, TelegramNotifier
        return TelegramNotifier(TelegramConfig(**config))

    raise ValueError(f"Unknown notifier type: {notifier_type!r}")
