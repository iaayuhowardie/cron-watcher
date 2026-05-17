from typing import Optional, Any


def get_notifier(notifier_type: str, **kwargs) -> Optional[Any]:
    ntype = notifier_type.lower()

    if ntype == "email":
        from cron_watcher.notifiers.email_notifier import EmailConfig, EmailNotifier
        return EmailNotifier(EmailConfig(**kwargs))

    if ntype == "slack":
        from cron_watcher.notifiers.slack_notifier import SlackConfig, SlackNotifier
        return SlackNotifier(SlackConfig(**kwargs))

    if ntype == "webhook":
        from cron_watcher.notifiers.webhook_notifier import WebhookConfig, WebhookNotifier
        return WebhookNotifier(WebhookConfig(**kwargs))

    if ntype == "pagerduty":
        from cron_watcher.notifiers.pagerduty_notifier import PagerDutyConfig, PagerDutyNotifier
        return PagerDutyNotifier(PagerDutyConfig(**kwargs))

    if ntype == "opsgenie":
        from cron_watcher.notifiers.opsgenie_notifier import OpsGenieConfig, OpsGenieNotifier
        return OpsGenieNotifier(OpsGenieConfig(**kwargs))

    if ntype == "log":
        from cron_watcher.notifiers.log_notifier import LogConfig, LogNotifier
        return LogNotifier(LogConfig(**kwargs))

    if ntype == "teams":
        from cron_watcher.notifiers.teams_notifier import TeamsConfig, TeamsNotifier
        return TeamsNotifier(TeamsConfig(**kwargs))

    if ntype == "discord":
        from cron_watcher.notifiers.discord_notifier import DiscordConfig, DiscordNotifier
        return DiscordNotifier(DiscordConfig(**kwargs))

    if ntype == "telegram":
        from cron_watcher.notifiers.telegram_notifier import TelegramConfig, TelegramNotifier
        return TelegramNotifier(TelegramConfig(**kwargs))

    if ntype == "sms":
        from cron_watcher.notifiers.sms_notifier import SMSConfig, SMSNotifier
        return SMSNotifier(SMSConfig(**kwargs))

    if ntype == "victorops":
        from cron_watcher.notifiers.victorops_notifier import VictorOpsConfig, VictorOpsNotifier
        return VictorOpsNotifier(VictorOpsConfig(**kwargs))

    if ntype == "sns":
        from cron_watcher.notifiers.sns_notifier import SNSConfig, SNSNotifier
        return SNSNotifier(SNSConfig(**kwargs))

    if ntype == "mattermost":
        from cron_watcher.notifiers.mattermost_notifier import MattermostConfig, MattermostNotifier
        return MattermostNotifier(MattermostConfig(**kwargs))

    if ntype == "gotify":
        from cron_watcher.notifiers.gotify_notifier import GotifyConfig, GotifyNotifier
        return GotifyNotifier(GotifyConfig(**kwargs))

    if ntype == "pushover":
        from cron_watcher.notifiers.pushover_notifier import PushoverConfig, PushoverNotifier
        return PushoverNotifier(PushoverConfig(**kwargs))

    if ntype == "ntfy":
        from cron_watcher.notifiers.ntfy_notifier import NtfyConfig, NtfyNotifier
        return NtfyNotifier(NtfyConfig(**kwargs))

    if ntype == "pushbullet":
        from cron_watcher.notifiers.pushbullet_notifier import PushbulletConfig, PushbulletNotifier
        return PushbulletNotifier(PushbulletConfig(**kwargs))

    if ntype == "rocketchat":
        from cron_watcher.notifiers.rocketchat_notifier import RocketChatConfig, RocketChatNotifier
        return RocketChatNotifier(RocketChatConfig(**kwargs))

    if ntype == "zulip":
        from cron_watcher.notifiers.zulip_notifier import ZulipConfig, ZulipNotifier
        return ZulipNotifier(ZulipConfig(**kwargs))

    if ntype == "matrix":
        from cron_watcher.notifiers.matrix_notifier import MatrixConfig, MatrixNotifier
        return MatrixNotifier(MatrixConfig(**kwargs))

    if ntype == "datadog":
        from cron_watcher.notifiers.datadog_notifier import DatadogConfig, DatadogNotifier
        return DatadogNotifier(DatadogConfig(**kwargs))

    if ntype == "splunk":
        from cron_watcher.notifiers.splunk_notifier import SplunkConfig, SplunkNotifier
        return SplunkNotifier(SplunkConfig(**kwargs))

    if ntype == "newrelic":
        from cron_watcher.notifiers.newrelic_notifier import NewRelicConfig, NewRelicNotifier
        return NewRelicNotifier(NewRelicConfig(**kwargs))

    if ntype == "grafana":
        from cron_watcher.notifiers.grafana_notifier import GrafanaConfig, GrafanaNotifier
        return GrafanaNotifier(GrafanaConfig(**kwargs))

    if ntype == "signalwire":
        from cron_watcher.notifiers.signalwire_notifier import SignalWireConfig, SignalWireNotifier
        return SignalWireNotifier(SignalWireConfig(**kwargs))

    if ntype == "mailgun":
        from cron_watcher.notifiers.mailgun_notifier import MailgunConfig, MailgunNotifier
        return MailgunNotifier(MailgunConfig(**kwargs))

    if ntype == "sendgrid":
        from cron_watcher.notifiers.sendgrid_notifier import SendGridConfig, SendGridNotifier
        return SendGridNotifier(SendGridConfig(**kwargs))

    if ntype == "hipchat":
        from cron_watcher.notifiers.hipchat_notifier import HipChatConfig, HipChatNotifier
        return HipChatNotifier(HipChatConfig(**kwargs))

    if ntype == "twilio":
        from cron_watcher.notifiers.twilio_notifier import TwilioConfig, TwilioNotifier
        return TwilioNotifier(TwilioConfig(**kwargs))

    if ntype == "influxdb":
        from cron_watcher.notifiers.influxdb_notifier import InfluxDBConfig, InfluxDBNotifier
        return InfluxDBNotifier(InfluxDBConfig(**kwargs))

    return None
