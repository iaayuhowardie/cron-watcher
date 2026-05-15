"""Tests for the AWS SNS notifier."""

from unittest.mock import MagicMock, patch
import pytest

from cron_watcher.notifiers.sns_notifier import SNSConfig, SNSNotifier


@pytest.fixture()
def sns_config() -> SNSConfig:
    return SNSConfig(
        topic_arn="arn:aws:sns:us-east-1:123456789012:cron-alerts",
        region="us-east-1",
        aws_access_key_id="AKIAIOSFODNN7EXAMPLE",
        aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    )


@pytest.fixture()
def notifier(sns_config: SNSConfig) -> SNSNotifier:
    with patch("cron_watcher.notifiers.sns_notifier.boto3") as mock_boto3:
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        instance = SNSNotifier(sns_config)
        instance._client = mock_client
        return instance


def _mock_response(notifier: SNSNotifier, *, raises=None):
    """Configure the underlying mock client."""
    if raises:
        notifier._client.publish.side_effect = raises
    else:
        notifier._client.publish.side_effect = None
        notifier._client.publish.return_value = {"MessageId": "abc-123"}


def test_send_returns_true_on_success(notifier: SNSNotifier) -> None:
    _mock_response(notifier)
    assert notifier.send("Test subject", "Test message") is True


def test_send_publishes_to_correct_topic(notifier: SNSNotifier, sns_config: SNSConfig) -> None:
    _mock_response(notifier)
    notifier.send("Job failed", "backup_job missed its schedule")
    call_kwargs = notifier._client.publish.call_args[1]
    assert call_kwargs["TopicArn"] == sns_config.topic_arn
    assert "backup_job missed its schedule" == call_kwargs["Message"]


def test_send_prepends_subject_prefix(notifier: SNSNotifier) -> None:
    _mock_response(notifier)
    notifier.send("Job failed", "details")
    call_kwargs = notifier._client.publish.call_args[1]
    assert call_kwargs["Subject"].startswith("[cron-watcher]")


def test_send_truncates_long_subject(notifier: SNSNotifier) -> None:
    _mock_response(notifier)
    long_subject = "x" * 200
    notifier.send(long_subject, "details")
    call_kwargs = notifier._client.publish.call_args[1]
    assert len(call_kwargs["Subject"]) <= 100


def test_send_returns_false_on_client_error(notifier: SNSNotifier) -> None:
    import botocore.exceptions
    _mock_response(notifier, raises=botocore.exceptions.ClientError(
        {"Error": {"Code": "AuthorizationError", "Message": "Access denied"}},
        "Publish",
    ))
    assert notifier.send("subject", "message") is False


def test_send_returns_false_on_botocore_error(notifier: SNSNotifier) -> None:
    import botocore.exceptions
    _mock_response(notifier, raises=botocore.exceptions.BotoCoreError())
    assert notifier.send("subject", "message") is False


def test_raises_import_error_when_boto3_missing(sns_config: SNSConfig) -> None:
    with patch("cron_watcher.notifiers.sns_notifier.boto3", None):
        with pytest.raises(ImportError, match="boto3"):
            SNSNotifier(sns_config)
