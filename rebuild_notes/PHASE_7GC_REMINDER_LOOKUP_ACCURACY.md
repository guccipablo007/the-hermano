# Phase 7G-C: Reminder Lookup Accuracy

Problem:
Hermes answered reminder lookup questions from stale memory/model context instead of actual cron storage.

Fix:
- Created `/root/.hermes/scripts/hermes_reminder_lookup.py`.
- Supported modes: `list`, `search`, `next`, `status`.
- Patched Telegram gateway with a read-only reminder lookup pre-router before generic model routing.
- Natural questions like `When is my next Mickey class reminder?` now call cron storage lookup directly.
- Natural questions like `When is my next Sunday upload reminder?` now return job `965330683cdb` with `2026-05-17T18:00:00+08:00`.
- Tightened multi-token matching so `Sunday upload` does not return Tuesday upload jobs.

Verification:
- Mickey lookup: VERIFIED from cron storage.
- Sunday upload lookup: VERIFIED from cron storage.
- Sunday upload status: VERIFIED, schedule `every Sunday at 18:00`.
- Nonexistent reminder lookup: NOT VERIFIED.
- Recurring reminder regression passed.
- One-shot create and delivery regressions passed.
- Quick/deep healthchecks passed.

No private route activated.
No default model changed.
No Gmail or YouTube configuration changed.
No full Telegram chat_id exposed.
