# Phase 7E: Verification Gate

Created/updated:
- `/root/.hermes/skills/verification-gate/SKILL.md`
- `/root/.hermes/scripts/hermes_verify_claim.py`

Purpose:
Prevent fake success claims. Hermes must only say done/fixed/sent/scheduled/created/delivered/verified/completed/updated/restarted/backed up when evidence exists.

Script modes:
- `file-exists`
- `service-active`
- `command-contains`
- `job-status`
- `latest-backup`
- `--help`

Safety:
- Masks bot tokens, bearer tokens, API keys, passwords, secrets, and Telegram chat IDs.
- Missing or ambiguous evidence returns `NOT VERIFIED`.

No default model changed. No Gmail/YouTube/private_data changes. Reminder system untouched.
