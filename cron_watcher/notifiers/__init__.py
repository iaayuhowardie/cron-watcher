from cron_watcher.notifiers.email_notifier import EmailNotifier
from cron_watcher.notifiers.slack_notifier import SlackNotifier
from cron_watcher.notifiers.webhook_notifier import WebhookNotifier

__all__ = ["EmailNotifier", "SlackNotifier", "WebhookNotifier"]


def get_notifier(notifier_type: str, **kwargs):
    """Factory function to get a notifier instance by type name.

    Args:
        notifier_type: The type of notifier to create. One of 'email',
            'slack', or 'webhook'.
        **kwargs: Keyword arguments passed to the notifier's constructor.

    Returns:
        An instance of the requested notifier.

    Raises:
        ValueError: If the notifier_type is not recognized.
    """
    notifiers = {
        "email": EmailNotifier,
        "slack": SlackNotifier,
        "webhook": WebhookNotifier,
    }
    if notifier_type not in notifiers:
        raise ValueError(
            f"Unknown notifier type '{notifier_type}'. "
            f"Valid options are: {', '.join(notifiers.keys())}"
        )
    return notifiers[notifier_type](**kwargs)
