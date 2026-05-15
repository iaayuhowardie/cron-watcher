from typing import Any, Dict


def get_notifier(notifier_type: str, config: Dict[str, Any]):
    """
    Factory that returns an instantiated notifier for the given type.

    :param notifier_type: One of email, slack, webhook, pagerduty, opsgenie,
                          log, teams, discord, telegram, sms, victorops.
    :param config: Dictionary of configuration values for the notifier.
    :returns: Instantiated notifier object with a ``send(subject, body)`` method.
    :raises ValueError: If the notifier type is unknown.
    """
    if notifier_type == "email":
        from cron_watcher.notifiers.email_notifier import EmailConfig, EmailNotifier
        return EmailNotifier(EmailConfig(**config))
    elif notifier_type == "slack":
        from cron_watcher.notifiers.slack_notifier import SlackConfig, SlackNotifier
        return SlackNotifier(SlackConfig(**config))
    elif notifier_type == "webhook":
        from cron_watcher.notifiers.webhook_notifier import WebhookConfig, WebhookNotifier
        return WebhookNotifier(WebhookConfig(**config))
    elif notifier_type == "pagerduty":
        from cron_watcher.notifiers.pagerduty_notifier import PagerDutyConfig, PagerDutyNotifier
        return PagerDutyNotifier(PagerDutyConfig(**config))
    elif notifier_type == "opsgenie":
        from cron_watcher.notifiers.opsgenie_notifier import OpsGenieConfig, OpsGenieNotifier
        return OpsGenieNotifier(OpsGenieConfig(**config))
    elif notifier_type == "log":
        from cron_watcher.notifiers.log_notifier import LogConfig, LogNotifier
        return LogNotifier(LogConfig(**config))
    elif notifier_type == "teams":
        from cron_watcher.notifiers.teams_notifier import TeamsConfig, TeamsNotifier
        return TeamsNotifier(TeamsConfig(**config))
    elif notifier_type == "discord":
        from cron_watcher.notifiers.discord_notifier import DiscordConfig, DiscordNotifier
        return DiscordNotifier(DiscordConfig(**config))
    elif notifier_type == "telegram":
        from cron_watcher.notifiers.telegram_notifier import TelegramConfig, TelegramNotifier
        return TelegramNotifier(TelegramConfig(**config))
    elif notifier_type == "sms":
        from cron_watcher.notifiers.sms_notifier import SMSConfig, SMSNotifier
        return SMSNotifier(SMSConfig(**config))
    elif notifier_type == "victorops":
        from cron_watcher.notifiers.victorops_notifier import VictorOpsConfig, VictorOpsNotifier
        return VictorOpsNotifier(VictorOpsConfig(**config))
    else:
        raise ValueError(f"Unknown notifier type: {notifier_type!r}")
