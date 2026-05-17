from typing import Any, Dict, Optional


def get_notifier(notifier_type: str, config: Dict[str, Any]) -> Optional[Any]:
    """Return an instantiated notifier for the given type, or None if unknown."""
    key = notifier_type.lower()

    if key == "email":
        from cron_watcher.notifiers.email_notifier import EmailConfig, EmailNotifier
        cfg = EmailConfig(**config)
        return EmailNotifier(cfg)

    if key == "slack":
        from cron_watcher.notifiers.slack_notifier import SlackConfig, SlackNotifier
        cfg = SlackConfig(**config)
        return SlackNotifier(cfg)

    if key == "webhook":
        from cron_watcher.notifiers.webhook_notifier import WebhookConfig, WebhookNotifier
        cfg = WebhookConfig(**config)
        return WebhookNotifier(cfg)

    if key == "pagerduty":
        from cron_watcher.notifiers.pagerduty_notifier import PagerDutyConfig, PagerDutyNotifier
        cfg = PagerDutyConfig(**config)
        return PagerDutyNotifier(cfg)

    if key == "opsgenie":
        from cron_watcher.notifiers.opsgenie_notifier import OpsGenieConfig, OpsGenieNotifier
        cfg = OpsGenieConfig(**config)
        return OpsGenieNotifier(cfg)

    if key == "log":
        from cron_watcher.notifiers.log_notifier import LogConfig, LogNotifier
        cfg = LogConfig(**config)
        return LogNotifier(cfg)

    if key == "teams":
        from cron_watcher.notifiers.teams_notifier import TeamsConfig, TeamsNotifier
        cfg = TeamsConfig(**config)
        return TeamsNotifier(cfg)

    if key == "discord":
        from cron_watcher.notifiers.discord_notifier import DiscordConfig, DiscordNotifier
        cfg = DiscordConfig(**config)
        return DiscordNotifier(cfg)

    if key == "telegram":
        from cron_watcher.notifiers.telegram_notifier import TelegramConfig, TelegramNotifier
        cfg = TelegramConfig(**config)
        return TelegramNotifier(cfg)

    if key == "sms":
        from cron_watcher.notifiers.sms_notifier import SMSConfig, SMSNotifier
        cfg = SMSConfig(**config)
        return SMSNotifier(cfg)

    if key == "victorops":
        from cron_watcher.notifiers.victorops_notifier import VictorOpsConfig, VictorOpsNotifier
        cfg = VictorOpsConfig(**config)
        return VictorOpsNotifier(cfg)

    if key == "sns":
        from cron_watcher.notifiers.sns_notifier import SNSConfig, SNSNotifier
        cfg = SNSConfig(**config)
        return SNSNotifier(cfg)

    if key == "mattermost":
        from cron_watcher.notifiers.mattermost_notifier import MattermostConfig, MattermostNotifier
        cfg = MattermostConfig(**config)
        return MattermostNotifier(cfg)

    if key == "gotify":
        from cron_watcher.notifiers.gotify_notifier import GotifyConfig, GotifyNotifier
        cfg = GotifyConfig(**config)
        return GotifyNotifier(cfg)

    if key == "pushover":
        from cron_watcher.notifiers.pushover_notifier import PushoverConfig, PushoverNotifier
        cfg = PushoverConfig(**config)
        return PushoverNotifier(cfg)

    if key == "ntfy":
        from cron_watcher.notifiers.ntfy_notifier import NtfyConfig, NtfyNotifier
        cfg = NtfyConfig(**config)
        return NtfyNotifier(cfg)

    if key == "pushbullet":
        from cron_watcher.notifiers.pushbullet_notifier import PushbulletConfig, PushbulletNotifier
        cfg = PushbulletConfig(**config)
        return PushbulletNotifier(cfg)

    if key == "rocketchat":
        from cron_watcher.notifiers.rocketchat_notifier import RocketChatConfig, RocketChatNotifier
        cfg = RocketChatConfig(**config)
        return RocketChatNotifier(cfg)

    if key == "zulip":
        from cron_watcher.notifiers.zulip_notifier import ZulipConfig, ZulipNotifier
        cfg = ZulipConfig(**config)
        return ZulipNotifier(cfg)

    if key == "matrix":
        from cron_watcher.notifiers.matrix_notifier import MatrixConfig, MatrixNotifier
        cfg = MatrixConfig(**config)
        return MatrixNotifier(cfg)

    if key == "datadog":
        from cron_watcher.notifiers.datadog_notifier import DatadogConfig, DatadogNotifier
        cfg = DatadogConfig(**config)
        return DatadogNotifier(cfg)

    if key == "splunk":
        from cron_watcher.notifiers.splunk_notifier import SplunkConfig, SplunkNotifier
        cfg = SplunkConfig(**config)
        return SplunkNotifier(cfg)

    if key == "newrelic":
        from cron_watcher.notifiers.newrelic_notifier import NewRelicConfig, NewRelicNotifier
        cfg = NewRelicConfig(**config)
        return NewRelicNotifier(cfg)

    if key == "grafana":
        from cron_watcher.notifiers.grafana_notifier import GrafanaConfig, GrafanaNotifier
        cfg = GrafanaConfig(**config)
        return GrafanaNotifier(cfg)

    return None
