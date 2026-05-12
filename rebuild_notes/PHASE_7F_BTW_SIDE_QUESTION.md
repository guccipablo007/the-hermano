# Phase 7F: /btw Side Question

Created:
- `/root/.hermes/scripts/hermes_btw_handler.py`
- `/root/.hermes/skills/btw-side-question/SKILL.md`

Behavior:
- `/btw` is treated as a read-only side question.
- Project history questions use Session Recall.
- Backup claims use Verification Gate.
- Risky actions are blocked and not executed.
- Secrets and full Telegram chat IDs are masked.

Telegram integration:
- Patched gateway pre-router before artifact/generic model routing.
- `/btw` replies to the same Telegram chat and returns early.

No default model changed. No Gmail/YouTube/private_data changes. Reminder system untouched.
