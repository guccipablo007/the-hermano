# Phase 7G-F: Reminder Update Root Cause and Verification

Problem:
A Telegram reminder update produced a friendly next-reminder answer with an inconsistent weekday/date combination and exposed raw cronjob/tool output.

Root cause:
- `cronjob(action="update")` returned a raw JSON-shaped success response without the same explicit verified envelope used by creates.
- The update path did not fail closed with a storage reload verification record before user-facing response composition.
- The normal Telegram sanitizer did not catch all raw cronjob call forms, single-line tool JSON, or call IDs.
- The friendly lookup formatter itself derives weekday from `next_run_at`, so the mismatch was most likely model-composed text after update, not the lookup formatter.

Fix:
- Added `_verify_updated_job()` to reload the updated job from cron storage.
- `cronjob(action="update")` now returns `verified: true`, timezone metadata, masked delivery, and stored `next_run_at` only after verification passes.
- Update now supports `end_date` consistently by storing it in the schedule for recurrence bounds.
- Strengthened Telegram user-visible sanitizer for raw cronjob calls, raw JSON payloads, call IDs, full chat IDs, tokens, and API-key-shaped values.
- Added `/root/.hermes/scripts/hermes_reminder_update_test.py` with generic reminder fixtures only.

Verification:
- Generic update weekday-set test passed.
- Same-day future update test passed.
- Same-day past update test passed.
- Multi-day weekly update test passed.
- End-date boundary update test passed.
- Invalid update failed closed.
- Formatter consistency test passed.
- Sanitizer regression test passed.

No private route activated.
No default model changed.
No scenario-specific reminder names hardcoded.
