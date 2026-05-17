from typing import Any, Dict, Optional


def get_notifier(notifier_type: str, config: Dict[str, Any]) -> Optional[Any]:
    t = notifier_type.lower()

    if t == "email":
        from cron_watcher.notifiers.email_notifier import EmailConfig, EmailNotifier
        return EmailNotifier(EmailConfig(**config))

    if t == "slack":
        from cron_watcher.notifiers.slack_notifier import SlackConfig, SlackNotifier
        return SlackNotifier(SlackConfig(**config))

    if t == "webhook":
        from cron_watcher.notifiers.webhook_notifier import WebhookConfig, WebhookNotifier
        return WebhookNotifier(WebhookConfig(**config))

    if t == "pagerduty":
        from cron_watcher.notifiers.pagerduty_notifier import PagerDutyConfig, PagerDutyNotifier
        return PagerDutyNotifier(PagerDutyConfig(**config))

    if t == "opsgenie":
        from cron_watcher.notifiers.opsgenie_notifier import OpsGenieConfig, OpsGenieNotifier
        return OpsGenieNotifier(OpsGenieConfig(**config))

    if t == "log":
        from cron_watcher.notifiers.log_notifier import LogConfig, LogNotifier
        return LogNotifier(LogConfig(**config))

    if t == "teams":
        from cron_watcher.notifiers.teams_notifier import TeamsConfig, TeamsNotifier
        return TeamsNotifier(TeamsConfig(**config))

    if t == "discord":
        from cron_watcher.notifiers.discord_notifier import DiscordConfig, DiscordNotifier
        return DiscordNotifier(DiscordConfig(**config))

    if t == "telegram":
        from cron_watcher.notifiers.telegram_notifier import TelegramConfig, TelegramNotifier
        return TelegramNotifier(TelegramConfig(**config))

    if t == "sms":
        from cron_watcher.notifiers.sms_notifier import SMSConfig, SMSNotifier
        return SMSNotifier(SMSConfig(**config))

    if t == "victorops":
        from cron_watcher.notifiers.victorops_notifier import VictorOpsConfig, VictorOpsNotifier
        return VictorOpsNotifier(VictorOpsConfig(**config))

    if t == "sns":
        from cron_watcher.notifiers.sns_notifier import SNSConfig, SNSNotifier
        return SNSNotifier(SNSConfig(**config))

    if t == "mattermost":
        from cron_watcher.notifiers.mattermost_notifier import MattermostConfig, MattermostNotifier
        return MattermostNotifier(MattermostConfig(**config))

    if t == "gotify":
        from cron_watcher.notifiers.gotify_notifier import GotifyConfig, GotifyNotifier
        return GotifyNotifier(GotifyConfig(**config))

    if t == "pushover":
        from cron_watcher.notifiers.pushover_notifier import PushoverConfig, PushoverNotifier
        return PushoverNotifier(PushoverConfig(**config))

    if t == "ntfy":
        from cron_watcher.notifiers.ntfy_notifier import NtfyConfig, NtfyNotifier
        return NtfyNotifier(NtfyConfig(**config))

    if t == "pushbullet":
        from cron_watcher.notifiers.pushbullet_notifier import PushbulletConfig, PushbulletNotifier
        return PushbulletNotifier(PushbulletConfig(**config))

    if t == "rocketchat":
        from cron_watcher.notifiers.rocketchat_notifier import RocketChatConfig, RocketChatNotifier
        return RocketChatNotifier(RocketChatConfig(**config))

    if t == "zulip":
        from cron_watcher.notifiers.zulip_notifier import ZulipConfig, ZulipNotifier
        return ZulipNotifier(ZulipConfig(**config))

    if t == "matrix":
        from cron_watcher.notifiers.matrix_notifier import MatrixConfig, MatrixNotifier
        return MatrixNotifier(MatrixConfig(**config))

    if t == "datadog":
        from cron_watcher.notifiers.datadog_notifier import DatadogConfig, DatadogNotifier
        return DatadogNotifier(DatadogConfig(**config))

    if t == "splunk":
        from cron_watcher.notifiers.splunk_notifier import SplunkConfig, SplunkNotifier
        return SplunkNotifier(SplunkConfig(**config))

    if t == "newrelic":
        from cron_watcher.notifiers.newrelic_notifier import NewRelicConfig, NewRelicNotifier
        return NewRelicNotifier(NewRelicConfig(**config))

    if t == "grafana":
        from cron_watcher.notifiers.grafana_notifier import GrafanaConfig, GrafanaNotifier
        return GrafanaNotifier(GrafanaConfig(**config))

    if t == "signalwire":
        from cron_watcher.notifiers.signalwire_notifier import SignalWireConfig, SignalWireNotifier
        return SignalWireNotifier(SignalWireConfig(**config))

    if t == "mailgun":
        from cron_watcher.notifiers.mailgun_notifier import MailgunConfig, MailgunNotifier
        return MailgunNotifier(MailgunConfig(**config))

    if t == "sendgrid":
        from cron_watcher.notifiers.sendgrid_notifier import SendGridConfig, SendGridNotifier
        return SendGridNotifier(SendGridConfig(**config))

    if t == "hipchat":
        from cron_watcher.notifiers.hipchat_notifier import HipChatConfig, HipChatNotifier
        return HipChatNotifier(HipChatConfig(**config))

    if t == "twilio":
        from cron_watcher.notifiers.twilio_notifier import TwilioConfig, TwilioNotifier
        return TwilioNotifier(TwilioConfig(**config))

    if t == "influxdb":
        from cron_watcher.notifiers.influxdb_notifier import InfluxDBConfig, InfluxDBNotifier
        return InfluxDBNotifier(InfluxDBConfig(**config))

    if t == "googlechat":
        from cron_watcher.notifiers.googlechat_notifier import GoogleChatConfig, GoogleChatNotifier
        return GoogleChatNotifier(GoogleChatConfig(**config))

    if t == "bearychat":
        from cron_watcher.notifiers.bearychat_notifier import BearyChatConfig, BearyChatNotifier
        return BearyChatNotifier(BearyChatConfig(**config))

    if t == "lark":
        from cron_watcher.notifiers.lark_notifier import LarkConfig, LarkNotifier
        return LarkNotifier(LarkConfig(**config))

    if t == "line":
        from cron_watcher.notifiers.line_notifier import LineConfig, LineNotifier
        return LineNotifier(LineConfig(**config))

    return None
