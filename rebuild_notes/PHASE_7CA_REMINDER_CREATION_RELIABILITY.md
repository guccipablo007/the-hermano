# Phase 7C-A: Telegram Reminder Creation Reliability

Problem:
Natural-language Telegram reminders were allowed to rely on model-estimated absolute times. This caused bad math for relative reminders and allowed false success claims.

Root cause:
`tools/cronjob_tools.py` trusted the model-provided `schedule` parameter. If the model converted `in 8 minutes` or `in 2 minutes` incorrectly before tool call, cron stored the incorrect time and reported success.

Fix:
- Added deterministic one-shot reminder parsing inside `cronjob(action="create")`.
- Relative reminders like `in 2 minutes` and `in 8 minutes` are computed in Asia/Shanghai with Python timedelta.
- `today/tonight/tomorrow at <time>` reminders are computed deterministically in Asia/Shanghai.
- Added post-create verification that the job exists in cron storage and `next_run_at` is future.
- Added `/root/.hermes/scripts/hermes_reminder_create_test.py`.

No Gmail/YouTube/private route changes.
No default model changed.
