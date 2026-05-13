# /btw Side Question

## Purpose

Use this for side questions beginning with `/btw`.

## Rules

- Keep answers brief.
- Do not derail the active project or phase.
- Read-only by default.
- Use Session Recall for project-history questions.
- Use Verification Gate for factual claims.
- Do not expose secrets.
- Do not expose full Telegram chat_id.
- Do not perform risky actions from `/btw`.
- If evidence is missing, say `NOT VERIFIED`.

## Examples

```bash
python3 /root/.hermes/scripts/hermes_btw_handler.py "/btw what did we fix in Phase 7E?"
python3 /root/.hermes/scripts/hermes_btw_handler.py "/btw what is the latest backup commit?"
python3 /root/.hermes/scripts/hermes_btw_handler.py "/btw search reminder failure"
```

## Friendly Output Rule - Phase 7H

Default `/btw` replies must be concise, natural Telegram text.

Rules:
- Do not show helper labels such as `SESSION_RECALL_PHASE=PASSED`, `VERIFIED`, or raw file paths by default.
- Summarize verified evidence from local records.
- Preserve raw/debug/technical output only when explicitly requested.
- Keep `/btw` read-only by default.
- Block risky actions from `/btw` instead of executing them.
- Never expose secrets, full chat IDs, tokens, API keys, passwords, or OAuth data.
