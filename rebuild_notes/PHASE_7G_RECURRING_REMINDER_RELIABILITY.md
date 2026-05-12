# Phase 7G: Recurring Reminder Reliability

Problem:
- Natural weekly recurring reminders skipped same-day future runs.
- Bad fallback one-shot reminders were created after a verified recurring success.
- Raw tool/debug output leaked into Telegram replies.
- Sunday upload reminder job was firing daily because the cron expression lacked a Sunday-only weekday field.

Fix:
- Added deterministic natural weekly parsing in /usr/local/lib/hermes-agent/cron/jobs.py.
- Added Asia/Shanghai-aware next-run computation for weekly schedules.
- Added end_date support as an upper bound for recurring jobs.
- Added /root/.hermes/scripts/hermes_recurring_reminder_test.py.
- Patched cronjob tool display to report end-dated recurring jobs as repeat=until.
- Patched gateway response sanitizer to remove raw internal tool/debug payloads and mask chat IDs.
- Removed no active bad Mickey fallback jobs; created corrected Mickey recurring reminder.

Sunday upload audit:
- Job 965330683cdb uses `0 12,15,17 * * *`, which means every day at 12:00, 15:00, and 17:00, not Sunday-only.
- It was not deleted in this phase.

No private route activated.
No default model changed.
One-shot reminder regression preserved.
