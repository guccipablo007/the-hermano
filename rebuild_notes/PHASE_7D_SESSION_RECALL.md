# Phase 7D: Session Recall/Search

Created:
- `/root/.hermes/skills/session-recall/SKILL.md`
- `/root/.hermes/scripts/hermes_session_recall.py`

Purpose:
Search and summarize safe Hermes project context including rebuild notes, BOOT.md, skills, model routing, masked config, and the safe Git backup mirror.

Modes:
- `search <query>`
- `latest`
- `phase <phase>`
- `status`
- `--help`

Safety:
- Excludes token/OAuth/credential/private/generated paths.
- Masks tokens, API keys, passwords, bearer values, bot tokens, and Telegram chat IDs.
- Returns `NOT VERIFIED` when evidence is missing.

No default model changed. No Gmail/YouTube/private_data changes. Reminder system untouched.
