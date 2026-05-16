"""Notifier registry for cron-watcher."""
from __future__ import annotations

from typing import Any, Dict, Optional


def get_notifier(notifier_type: str, config: Dict[str, Any]) -> Optional[Any]:
    """Instantiate and return the appropriate notifier for *notifier_type*.

    Parameters
    ----------
    notifier_type:
        Identifier string, e.g. ``"email"``, ``"slack"``, ``"ntfy"``.
    config:
        Raw configuration dictionary for the notifier.

    Returns
    -------
    A notifier instance with a ``send(subject, body) -> bool`` method, or
    ``None`` when *notifier_type* is unknown.
    """
    notifier_type = notifier_type.lower()

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

    if notifier_type == "sms":
        from cron_watcher.notifiers.sms_notifier import SMSConfig, SMSNotifier
        return SMSNotifier(SMSConfig(**config))

    if notifier_type == "victorops":
        from cron_watcher.notifiers.victorops_notifier import VictorOpsConfig, VictorOpsNotifier
        return VictorOpsNotifier(VictorOpsConfig(**config))

    if notifier_type == "sns":
        from cron_watcher.notifiers.sns_notifier import SNSConfig, SNSNotifier
        return SNSNotifier(SNSConfig(**config))

    if notifier_type == "mattermost":
        from cron_watcher.notifiers.mattermost_notifier import MattermostConfig, MattermostNotifier
        return MattermostNotifier(MattermostConfig(**config))

    if notifier_type == "gotify":
        from cron_watcher.notifiers.gotify_notifier import GotifyConfig, GotifyNotifier
        return GotifyNotifier(GotifyConfig(**config))

    if notifier_type == "pushover":
        from cron_watcher.notifiers.pushover_notifier import PushoverConfig, PushoverNotifier
        return PushoverNotifier(PushoverConfig(**config))

    if notifier_type == "ntfy":
        from cron_watcher.notifiers.ntfy_notifier import NtfyConfig, NtfyNotifier
        return NtfyNotifier(NtfyConfig(**config))

    return None
