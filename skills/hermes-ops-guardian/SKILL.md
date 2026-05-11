# Hermes Ops Guardian

## Purpose

Protect Hermes from fake success, silent failure, broken cron, broken Telegram delivery, bad backups, and broken artifact scripts.

## Rules

- Before risky work, run `hermes_prechange_backup`.
- After gateway restart, run `hermes_ops_healthcheck`.
- If healthcheck fails, say `NOT VERIFIED` and report the failing check.
- Never claim success unless the action is verified by tool output, file existence, service status, or test result.
- Keep Gmail, YouTube, tokens, OAuth credentials, API keys, Telegram bot tokens, and `private_data` protected unless explicitly requested.
- Do not expose full Telegram chat IDs in normal replies; report only presence or masked IDs.
- Do not break the reminder scheduler or Telegram delivery path.
