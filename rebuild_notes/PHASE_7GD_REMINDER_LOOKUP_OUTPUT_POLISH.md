# Phase 7G-D: Reminder Lookup Telegram Output Polish

Problem:
Reminder lookup accuracy was fixed, but Telegram replies exposed raw technical labels such as VERIFIED, EARLIEST_NEXT_REMINDER, job_id, enabled/state, and delivery internals.

Fix:
- Added `--format raw|friendly` to `/root/.hermes/scripts/hermes_reminder_lookup.py`.
- Preserved raw technical output for debugging.
- Added friendly natural-language output for Telegram.
- Updated Telegram reminder lookup pre-router to call `--format friendly`.
- Friendly output formats China-time timestamps as weekday/month/day/year and AM/PM.
- Friendly output formats weekly schedules as readable sentences.
- Nonexistent lookup now returns a concise user-facing NOT VERIFIED message without raw diagnostics.

Verification:
- Mickey friendly CLI lookup passed.
- Sunday upload friendly CLI lookup passed.
- Nonexistent friendly lookup passed.
- Raw mode test passed.
- Recurring reminder regression passed.
- One-shot create and delivery regressions passed.
- Quick/deep healthchecks passed.

No private route activated.
No default model changed.
No Gmail or YouTube configuration changed.
No full Telegram chat_id exposed.
