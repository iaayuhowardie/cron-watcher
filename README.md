# cron-watcher

> Lightweight daemon that monitors cron job execution and sends alerts on failure or missed runs.

---

## Installation

```bash
pip install cron-watcher
```

Or install from source:

```bash
git clone https://github.com/yourname/cron-watcher.git && cd cron-watcher && pip install .
```

---

## Usage

Define your monitored jobs in a `cron-watcher.yaml` config file:

```yaml
jobs:
  - name: daily-backup
    schedule: "0 2 * * *"
    timeout: 300
    alert:
      email: ops@example.com

  - name: hourly-sync
    schedule: "0 * * * *"
    timeout: 60
    alert:
      slack_webhook: https://hooks.slack.com/services/your/webhook/url
```

Then start the daemon:

```bash
cron-watcher start --config cron-watcher.yaml
```

Wrap any existing cron command to report its status:

```bash
# In your crontab
0 2 * * * cron-watcher exec --job daily-backup -- /usr/local/bin/backup.sh
```

Check the status of all monitored jobs:

```bash
cron-watcher status
```

---

## How It Works

`cron-watcher` tracks job heartbeats and execution exit codes. If a job exceeds its expected schedule window or exits with a non-zero status, an alert is dispatched via the configured channel (email, Slack, or webhook).

---

## License

This project is licensed under the [MIT License](LICENSE).