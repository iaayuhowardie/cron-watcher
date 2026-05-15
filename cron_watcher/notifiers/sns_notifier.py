"""AWS SNS notifier for cron-watcher alerts."""

from dataclasses import dataclass
from typing import Optional

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    boto3 = None


@dataclass
class SNSConfig:
    topic_arn: str
    region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    subject_prefix: str = "[cron-watcher]"


class SNSNotifier:
    """Sends alert notifications via AWS SNS."""

    def __init__(self, config: SNSConfig) -> None:
        if boto3 is None:
            raise ImportError("boto3 is required for SNSNotifier: pip install boto3")
        self.config = config
        session_kwargs = {"region_name": config.region}
        if config.aws_access_key_id and config.aws_secret_access_key:
            session_kwargs["aws_access_key_id"] = config.aws_access_key_id
            session_kwargs["aws_secret_access_key"] = config.aws_secret_access_key
        self._client = boto3.client("sns", **session_kwargs)

    def send(self, subject: str, message: str) -> bool:
        """Publish a message to the configured SNS topic.

        Returns True on success, False on failure.
        """
        full_subject = f"{self.config.subject_prefix} {subject}"
        try:
            self._client.publish(
                TopicArn=self.config.topic_arn,
                Subject=full_subject[:100],  # SNS subject limit
                Message=message,
            )
            return True
        except (BotoCoreError, ClientError) as exc:
            print(f"SNSNotifier error: {exc}")
            return False
