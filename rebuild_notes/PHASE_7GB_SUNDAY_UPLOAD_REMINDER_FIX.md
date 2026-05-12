# Phase 7G-B: Sunday Upload Reminder Fix

Problem:
Job `965330683cdb` was named `Sunday 6 PM Upload Reminder`, but its schedule was `0 12,15,17 * * *`, which fires every day at 12:00, 15:00, and 17:00.

Fix:
- Updated job `965330683cdb` in place.
- Preserved existing Telegram origin delivery target.
- Changed prompt to: `Reminder: YouTube upload scheduled for 6:00 PM China time`.
- Changed schedule to natural weekly schedule: `every Sunday at 18:00`.
- Verified next run: `2026-05-17T18:00:00+08:00`.
- Extended recurring reminder regression test with Sunday-only weekly schedule.

Verification:
- `SUNDAY_ONLY_WEEKLY=PASSED`
- `RECURRING_REMINDER_TEST=PASSED`
- `REMINDER_CREATE_TEST=PASSED`
- `REMINDER_DELIVERY_TEST=PASSED`
- `OPS_HEALTHCHECK_QUICK=PASSED`
- `OPS_HEALTHCHECK_DEEP=PASSED`

No private route activated.
No default model changed.
No Gmail or YouTube configuration changed.
No full Telegram chat_id exposed.
Gateway restart was not required.
