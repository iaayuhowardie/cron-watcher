"""Command-line interface for cron-watcher."""

import argparse
import logging
import sys

from cron_watcher.config import load_config
from cron_watcher.watcher import Watcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cron-watcher",
        description="Monitor cron jobs and alert on failures or missed runs.",
    )
    parser.add_argument(
        "--config", "-c",
        default="cron_watcher.yaml",
        help="Path to configuration file (default: cron_watcher.yaml)",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("run", help="Start the watcher daemon")

    report = subparsers.add_parser("report", help="Report a job result")
    report.add_argument("job_name", help="Name of the cron job")
    report.add_argument(
        "--exit-code", type=int, default=0, help="Exit code of the job"
    )
    report.add_argument("--output", default="", help="Captured output of the job")

    return parser


def cmd_run(watcher: Watcher, args: argparse.Namespace) -> int:
    try:
        watcher.run(poll_interval=60)
    except KeyboardInterrupt:
        watcher.stop()
    return 0


def cmd_report(watcher: Watcher, args: argparse.Namespace) -> int:
    if args.exit_code == 0:
        watcher.report_success(args.job_name)
        logger.info("Recorded success for job '%s'", args.job_name)
    else:
        sent = watcher.report_failure(args.job_name, args.exit_code, args.output)
        if not sent:
            logger.error("Failed to send alert for job '%s'", args.job_name)
            return 1
    return 0


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    try:
        config = load_config(args.config)
    except FileNotFoundError:
        logger.error("Config file not found: %s", args.config)
        return 1
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to load config: %s", exc)
        return 1

    watcher = Watcher(config)

    if args.command == "run":
        return cmd_run(watcher, args)
    if args.command == "report":
        return cmd_report(watcher, args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
