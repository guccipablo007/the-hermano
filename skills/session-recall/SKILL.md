# Session Recall

## Purpose

Use this skill when Your Majesty asks what was done before, what changed, what phase we are on, what failed previously, or asks to recall project context.

## Rules

- Prefer local rebuild notes and verified status files over memory guesses.
- Use `/root/.hermes/scripts/hermes_session_recall.py` for evidence-backed recall.
- Never expose secrets.
- Mask chat IDs, tokens, keys, and passwords.
- If evidence is not found, say `NOT VERIFIED` instead of guessing.
- For technical history, cite the file path/source in the response.
- Keep summaries short unless Your Majesty asks for full details.

## Commands

```bash
python3 /root/.hermes/scripts/hermes_session_recall.py latest
python3 /root/.hermes/scripts/hermes_session_recall.py phase 7C
python3 /root/.hermes/scripts/hermes_session_recall.py search "reminder failure"
python3 /root/.hermes/scripts/hermes_session_recall.py status
```

## Safe Sources

- `/root/.hermes/rebuild_notes/`
- `/root/.hermes/BOOT.md`
- `/root/.hermes/skills/`
- `/root/.hermes/model_routing/`
- masked `/root/.hermes/config.yaml`
- safe files in `/root/hermano-backup`

Do not search token folders, OAuth files, `.env`, provider secret files, raw private account data, or generated outputs.

## Verification Gate

Recall summaries must cite local evidence. If evidence is missing, say `NOT VERIFIED` instead of guessing.
