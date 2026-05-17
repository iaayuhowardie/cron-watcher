from typing import Any, Dict, Optional


def get_notifier(notifier_type: str, config: Dict[str, Any]):
    key = notifier_type.lower()

    if key == "email":
        from .email_notifier import EmailConfig, EmailNotifier
        return EmailNotifier(EmailConfig(**config))

    if key == "slack":
        from .slack_notifier import SlackConfig, SlackNotifier
        return SlackNotifier(SlackConfig(**config))

    if key == "webhook":
        from .webhook_notifier import WebhookConfig, WebhookNotifier
        return WebhookNotifier(WebhookConfig(**config))

    if key == "pagerduty":
        from .pagerduty_notifier import PagerDutyConfig, PagerDutyNotifier
        return PagerDutyNotifier(PagerDutyConfig(**config))

    if key == "opsgenie":
        from .opsgenie_notifier import OpsGenieConfig, OpsGenieNotifier
        return OpsGenieNotifier(OpsGenieConfig(**config))

    if key == "log":
        from .log_notifier import LogConfig, LogNotifier
        return LogNotifier(LogConfig(**config))

    if key == "teams":
        from .teams_notifier import TeamsConfig, TeamsNotifier
        return TeamsNotifier(TeamsConfig(**config))

    if key == "discord":
        from .discord_notifier import DiscordConfig, DiscordNotifier
        return DiscordNotifier(DiscordConfig(**config))

    if key == "telegram":
        from .telegram_notifier import TelegramConfig, TelegramNotifier
        return TelegramNotifier(TelegramConfig(**config))

    if key == "sms":
        from .sms_notifier import SMSConfig, SMSNotifier
        return SMSNotifier(SMSConfig(**config))

    if key == "victorops":
        from .victorops_notifier import VictorOpsConfig, VictorOpsNotifier
        return VictorOpsNotifier(VictorOpsConfig(**config))

    if key == "sns":
        from .sns_notifier import SNSConfig, SNSNotifier
        return SNSNotifier(SNSConfig(**config))

    if key == "mattermost":
        from .mattermost_notifier import MattermostConfig, MattermostNotifier
        return MattermostNotifier(MattermostConfig(**config))

    if key == "gotify":
        from .gotify_notifier import GotifyConfig, GotifyNotifier
        return GotifyNotifier(GotifyConfig(**config))

    if key == "pushover":
        from .pushover_notifier import PushoverConfig, PushoverNotifier
        return PushoverNotifier(PushoverConfig(**config))

    if key == "ntfy":
        from .ntfy_notifier import NtfyConfig, NtfyNotifier
        return NtfyNotifier(NtfyConfig(**config))

    if key == "pushbullet":
        from .pushbullet_notifier import PushbulletConfig, PushbulletNotifier
        return PushbulletNotifier(PushbulletConfig(**config))

    if key == "rocketchat":
        from .rocketchat_notifier import RocketChatConfig, RocketChatNotifier
        return RocketChatNotifier(RocketChatConfig(**config))

    if key == "zulip":
        from .zulip_notifier import ZulipConfig, ZulipNotifier
        return ZulipNotifier(ZulipConfig(**config))

    if key == "matrix":
        from .matrix_notifier import MatrixConfig, MatrixNotifier
        return MatrixNotifier(MatrixConfig(**config))

    if key == "datadog":
        from .datadog_notifier import DatadogConfig, DatadogNotifier
        return DatadogNotifier(DatadogConfig(**config))

    if key == "splunk":
        from .splunk_notifier import SplunkConfig, SplunkNotifier
        return SplunkNotifier(SplunkConfig(**config))

    if key == "newrelic":
        from .newrelic_notifier import NewRelicConfig, NewRelicNotifier
        return NewRelicNotifier(NewRelicConfig(**config))

    if key == "grafana":
        from .grafana_notifier import GrafanaConfig, GrafanaNotifier
        return GrafanaNotifier(GrafanaConfig(**config))

    if key == "signalwire":
        from .signalwire_notifier import SignalWireConfig, SignalWireNotifier
        return SignalWireNotifier(SignalWireConfig(**config))

    if key == "mailgun":
        from .mailgun_notifier import MailgunConfig, MailgunNotifier
        return MailgunNotifier(MailgunConfig(**config))

    if key == "sendgrid":
        from .sendgrid_notifier import SendGridConfig, SendGridNotifier
        return SendGridNotifier(SendGridConfig(**config))

    if key == "hipchat":
        from .hipchat_notifier import HipChatConfig, HipChatNotifier
        return HipChatNotifier(HipChatConfig(**config))

    return None
