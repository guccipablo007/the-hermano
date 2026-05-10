# Phase 7C-TZ-B: Live Telegram China-Time Context

Changes:
- Injected hermes_time_context timezone prompt into normal Telegram model routing context.
- Created hermes_reminder_time_audit.py and /usr/local/bin/hermes_reminder_time_audit.
- Created /usr/local/bin/hermes_time_context wrapper.
- Created china-time-guardian skill.
- Set Hermes config timezone to Asia/Shanghai without changing model configuration.
- Patched cron.jobs naive ISO timestamp handling to use Hermes configured timezone.

Rules:
- Default user timezone is Asia/Shanghai / China time / UTC+08:00.
- CST means China Standard Time unless U.S. Central is explicitly stated.
- Reminder success requires real job existence and next-run verification.

No private route activated.
No default model changed.
