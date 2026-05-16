from typing import Any, Dict, Optional


def get_notifier(config: Dict[str, Any]) -> Optional[Any]:
    notifier_type = config.get("type", "").lower()

    if notifier_type == "email":
        from cron_watcher.notifiers.email_notifier import EmailConfig, EmailNotifier
        cfg = EmailConfig(**{k: v for k, v in config.items() if k != "type"})
        return EmailNotifier(cfg)

    if notifier_type == "slack":
        from cron_watcher.notifiers.slack_notifier import SlackConfig, SlackNotifier
        cfg = SlackConfig(**{k: v for k, v in config.items() if k != "type"})
        return SlackNotifier(cfg)

    if notifier_type == "webhook":
        from cron_watcher.notifiers.webhook_notifier import WebhookConfig, WebhookNotifier
        cfg = WebhookConfig(**{k: v for k, v in config.items() if k != "type"})
        return WebhookNotifier(cfg)

    if notifier_type == "pagerduty":
        from cron_watcher.notifiers.pagerduty_notifier import PagerDutyConfig, PagerDutyNotifier
        cfg = PagerDutyConfig(**{k: v for k, v in config.items() if k != "type"})
        return PagerDutyNotifier(cfg)

    if notifier_type == "opsgenie":
        from cron_watcher.notifiers.opsgenie_notifier import OpsGenieConfig, OpsGenieNotifier
        cfg = OpsGenieConfig(**{k: v for k, v in config.items() if k != "type"})
        return OpsGenieNotifier(cfg)

    if notifier_type == "log":
        from cron_watcher.notifiers.log_notifier import LogConfig, LogNotifier
        cfg = LogConfig(**{k: v for k, v in config.items() if k != "type"})
        return LogNotifier(cfg)

    if notifier_type == "teams":
        from cron_watcher.notifiers.teams_notifier import TeamsConfig, TeamsNotifier
        cfg = TeamsConfig(**{k: v for k, v in config.items() if k != "type"})
        return TeamsNotifier(cfg)

    if notifier_type == "discord":
        from cron_watcher.notifiers.discord_notifier import DiscordConfig, DiscordNotifier
        cfg = DiscordConfig(**{k: v for k, v in config.items() if k != "type"})
        return DiscordNotifier(cfg)

    if notifier_type == "telegram":
        from cron_watcher.notifiers.telegram_notifier import TelegramConfig, TelegramNotifier
        cfg = TelegramConfig(**{k: v for k, v in config.items() if k != "type"})
        return TelegramNotifier(cfg)

    if notifier_type == "sms":
        from cron_watcher.notifiers.sms_notifier import SMSConfig, SMSNotifier
        cfg = SMSConfig(**{k: v for k, v in config.items() if k != "type"})
        return SMSNotifier(cfg)

    if notifier_type == "victorops":
        from cron_watcher.notifiers.victorops_notifier import VictorOpsConfig, VictorOpsNotifier
        cfg = VictorOpsConfig(**{k: v for k, v in config.items() if k != "type"})
        return VictorOpsNotifier(cfg)

    if notifier_type == "sns":
        from cron_watcher.notifiers.sns_notifier import SNSConfig, SNSNotifier
        cfg = SNSConfig(**{k: v for k, v in config.items() if k != "type"})
        return SNSNotifier(cfg)

    if notifier_type == "mattermost":
        from cron_watcher.notifiers.mattermost_notifier import MattermostConfig, MattermostNotifier
        cfg = MattermostConfig(**{k: v for k, v in config.items() if k != "type"})
        return MattermostNotifier(cfg)

    if notifier_type == "gotify":
        from cron_watcher.notifiers.gotify_notifier import GotifyConfig, GotifyNotifier
        cfg = GotifyConfig(**{k: v for k, v in config.items() if k != "type"})
        return GotifyNotifier(cfg)

    if notifier_type == "pushover":
        from cron_watcher.notifiers.pushover_notifier import PushoverConfig, PushoverNotifier
        cfg = PushoverConfig(**{k: v for k, v in config.items() if k != "type"})
        return PushoverNotifier(cfg)

    if notifier_type == "ntfy":
        from cron_watcher.notifiers.ntfy_notifier import NtfyConfig, NtfyNotifier
        cfg = NtfyConfig(**{k: v for k, v in config.items() if k != "type"})
        return NtfyNotifier(cfg)

    if notifier_type == "pushbullet":
        from cron_watcher.notifiers.pushbullet_notifier import PushbulletConfig, PushbulletNotifier
        cfg = PushbulletConfig(**{k: v for k, v in config.items() if k != "type"})
        return PushbulletNotifier(cfg)

    if notifier_type == "rocketchat":
        from cron_watcher.notifiers.rocketchat_notifier import RocketChatConfig, RocketChatNotifier
        cfg = RocketChatConfig(**{k: v for k, v in config.items() if k != "type"})
        return RocketChatNotifier(cfg)

    if notifier_type == "zulip":
        from cron_watcher.notifiers.zulip_notifier import ZulipConfig, ZulipNotifier
        cfg = ZulipConfig(**{k: v for k, v in config.items() if k != "type"})
        return ZulipNotifier(cfg)

    return None
