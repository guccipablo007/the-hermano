# Phase 7G-G: Generic Reminder List Formatting

Problem:
Storage-backed friendly reminder list output still displayed raw cron fragments for cron-based reminders.

Root cause:
`friendly_schedule()` fell back to `schedule_text()` for cron jobs. That is correct for raw/debug mode, but friendly mode needs a natural-language translation or a safe generic fallback.

Fix:
- Added generic cron-to-friendly formatting in `/root/.hermes/scripts/hermes_reminder_lookup.py`.
- Friendly mode now translates simple daily and weekly cron expressions.
- Unsupported cron expressions show `Verified schedule from storage.` in friendly mode.
- Raw mode still exposes raw schedule text for debugging, with secrets/chat IDs masked.
- Added `/root/.hermes/scripts/hermes_reminder_lookup_format_test.py`.

Verification:
- Daily cron friendly test passed.
- Weekly Saturday cron friendly test passed.
- Weekly Sunday cron friendly tests passed.
- Unsupported cron hidden test passed.
- Raw mode preserved test passed.
- Friendly list contains no raw cron fragments.
- Reminder update, recurring, create, delivery, quick healthcheck, and deep healthcheck passed.

No private route activated.
No default model changed.
No reminder names hardcoded.
