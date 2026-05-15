"""Tests for the CLI module."""

from unittest.mock import MagicMock, patch

import pytest

from cron_watcher.cli import build_parser, main


CONFIG_CONTENT = "jobs:\n  - name: backup\n    schedule: '0 * * * *'\nalert:\n  method: log\n"


@pytest.fixture
def parser():
    return build_parser()


@pytest.fixture
def config_file(tmp_path):
    """Write a minimal valid config file and return its path."""
    path = tmp_path / "cron_watcher.yaml"
    path.write_text(CONFIG_CONTENT)
    return path


def test_parser_defaults(parser):
    args = parser.parse_args(["run"])
    assert args.command == "run"
    assert args.config == "cron_watcher.yaml"


def test_parser_custom_config(parser):
    args = parser.parse_args(["-c", "custom.yaml", "run"])
    assert args.config == "custom.yaml"


def test_parser_report_defaults(parser):
    args = parser.parse_args(["report", "backup"])
    assert args.job_name == "backup"
    assert args.exit_code == 0
    assert args.output == ""


def test_parser_report_with_failure(parser):
    args = parser.parse_args(["report", "backup", "--exit-code", "1", "--output", "err"])
    assert args.exit_code == 1
    assert args.output == "err"


def test_main_no_command_returns_1():
    result = main([])
    assert result == 1


def test_main_missing_config_returns_1():
    result = main(["-c", "nonexistent.yaml", "run"])
    assert result == 1


def test_main_report_success(config_file):
    with patch("cron_watcher.cli.Watcher") as MockWatcher:
        instance = MagicMock()
        MockWatcher.return_value = instance
        result = main(["-c", str(config_file), "report", "backup"])
    assert result == 0
    instance.report_success.assert_called_once_with("backup")


def test_main_report_failure_alert_sent(config_file):
    with patch("cron_watcher.cli.Watcher") as MockWatcher:
        instance = MagicMock()
        instance.report_failure.return_value = True
        MockWatcher.return_value = instance
        result = main(["-c", str(config_file), "report", "backup", "--exit-code", "2"])
    assert result == 0
    instance.report_failure.assert_called_once_with("backup", 2, "")


def test_main_report_failure_alert_not_sent_returns_1(config_file):
    with patch("cron_watcher.cli.Watcher") as MockWatcher:
        instance = MagicMock()
        instance.report_failure.return_value = False
        MockWatcher.return_value = instance
        result = main(["-c", str(config_file), "report", "backup", "--exit-code", "1"])
    assert result == 1
