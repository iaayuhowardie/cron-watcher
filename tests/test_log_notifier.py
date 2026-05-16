"""Tests for the log notifier."""

import logging
import pytest

from cron_watcher.notifiers.log_notifier import LogConfig, LogNotifier


@pytest.fixture()
def log_config() -> LogConfig:
    return LogConfig(log_level="WARNING")


@pytest.fixture()
def notifier(log_config: LogConfig) -> LogNotifier:
    # Reset handlers between tests to avoid duplicate output
    logger = logging.getLogger("cron_watcher.alerts")
    logger.handlers.clear()
    return LogNotifier(log_config)


def test_send_returns_true(notifier: LogNotifier) -> None:
    result = notifier.send("Test subject", "Test message")
    assert result is True


def test_send_emits_log_record(notifier: LogNotifier, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING, logger="cron_watcher.alerts"):
        notifier.send("Missed run", "Job backup did not run")

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert "Missed run" in record.message
    assert "Job backup did not run" in record.message


def test_send_to_file(tmp_path: pytest.TempPathFactory) -> None:
    log_file = str(tmp_path / "alerts.log")
    config = LogConfig(log_file=log_file, log_level="WARNING")

    logger = logging.getLogger("cron_watcher.alerts")
    logger.handlers.clear()

    file_notifier = LogNotifier(config)
    result = file_notifier.send("File alert", "Written to file")

    assert result is True
    with open(log_file) as fh:
        contents = fh.read()
    assert "File alert" in contents
    assert "Written to file" in contents


def test_default_config_uses_stdout() -> None:
    config = LogConfig()
    assert config.log_file is None
    assert config.log_level == "WARNING"


def test_handlers_not_duplicated() -> None:
    """Creating two notifiers with the same logger should not add duplicate handlers."""
    logger = logging.getLogger("cron_watcher.alerts")
    logger.handlers.clear()

    config = LogConfig()
    LogNotifier(config)
    LogNotifier(config)

    # The second instantiation finds existing handlers and skips adding more
    assert len(logger.handlers) == 1


def test_custom_log_level(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("cron_watcher.alerts")
    logger.handlers.clear()

    config = LogConfig(log_level="DEBUG")
    notifier = LogNotifier(config)

    with caplog.at_level(logging.DEBUG, logger="cron_watcher.alerts"):
        notifier.send("Debug subject", "Debug body")

    assert any("Debug subject" in r.message for r in caplog.records)


def test_send_emits_log_record_at_correct_level(notifier: LogNotifier, caplog: pytest.LogCaptureFixture) -> None:
    """Verify that the emitted log record uses the WARNING level by default."""
    with caplog.at_level(logging.WARNING, logger="cron_watcher.alerts"):
        notifier.send("Level check", "Should be WARNING")

    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.WARNING
