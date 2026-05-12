# Phase 7G-E: General Reminder Rules and Upload Schedule

Changes:
- Generalized reminder lookup/list behavior to read cron storage instead of memory.
- Removed scenario-specific lookup aliases for named reminders.
- Added generic friendly grouping for multi-offset reminders such as 6-hour, 3-hour, and 1-hour reminders.
- Added parser support for explicit absolute one-shot schedules like `once at 2026-05-14 15:30`.
- Updated Sunday YouTube upload reminders to three separate verified jobs:
  - 6-hour reminder: every Sunday at 12:00 China time.
  - 3-hour reminder: every Sunday at 15:00 China time.
  - 1-hour reminder: every Sunday at 17:00 China time.
- Paused obsolete Tuesday/Friday upload reminders and confirmed no active daily 12/15/17 upload reminder remains.
- Expanded recurring reminder regression tests for Sunday upload offsets, same-day future/past, end dates, absolute once-at, and bad parse handling.
- Expanded Telegram reminder lookup routing for list-all phrases such as "show me all my reminders".

Verification:
- RECURRING_REMINDER_TEST=PASSED.
- REMINDER_CREATE_TEST=PASSED.
- REMINDER_DELIVERY_TEST=PASSED.
- Storage-backed friendly list includes Mickey and the three Sunday upload reminders.
- Sunday upload next lookup returns 2026-05-17 12:00 China time as the next reminder and labels it as the 6-hour reminder.
- Mickey next lookup returns the verified stored next_run_at.

No private route activated.
No default model changed.
No raw Telegram chat IDs exposed.
