# Phase 7J-E2: Friendly Delegated Task Output

Problem:
Live Telegram delegated task status exposed raw JSON-like task ledger records and report paths.

Changed:
- /root/.hermes/scripts/hermes_agent_delegate.py
- /root/.hermes/scripts/hermes_live_natural_router.py

Behavior:
- Added `hermes_agent_delegate.py status --format friendly --limit N`.
- Preserved `status --format raw` for explicit raw/debug ledger requests.
- Friendly mode reads /root/.hermes/agent_tasks/tasks.jsonl and formats storage-backed records only.
- Friendly mode shows task summary, agent, verification status, task type, and Asia/Shanghai time.
- Friendly mode hides raw JSON, report paths, full task JSON, and job-id-like hex strings in summaries.
- Raw/debug mode remains sanitized and explicit only.
- Live natural router now routes ?Show recent delegated tasks? to friendly status directly.
- Live natural router routes ?Show raw delegated task ledger? to sanitized raw/debug output.

Safety preserved:
- Read-only delegated execution remains whitelist-based.
- Low-risk write gate remains unchanged.
- Risky actions remain blocked.
- Reminder query-first behavior remains storage-backed.
- No provider/model routing changed.
- No Gmail or YouTube configured.
- No private_data route activated.

Verification:
- Friendly ledger CLI passed.
- Raw ledger CLI passed.
- Live-router friendly task status passed.
- Read-only delegated task status regression passed.
- Low-risk write approval regression passed.
- Risky restart block regression passed.
- Model router, provider status, /btw, reminder intent guard, reminder update, recurring reminder, one-shot create, one-shot delivery, quick healthcheck, and deep healthcheck regressions passed.
