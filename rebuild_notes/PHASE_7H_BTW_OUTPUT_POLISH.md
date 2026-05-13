# Phase 7H: /btw Output Polish

Problem:
`/btw` side-question routing worked, but default replies exposed raw helper stdout such as `SESSION_RECALL_PHASE=PASSED` and rebuild-note paths.

Fix:
- Replaced truncation-style `/btw` output with friendly formatting in `/root/.hermes/scripts/hermes_btw_handler.py`.
- Added natural summaries for phase recall, search recall, latest backup commit, time context, model config, and quick health.
- Preserved raw/debug mode when explicitly requested.
- Kept `/btw` read-only and blocked risky actions.
- Continued masking tokens, API keys, passwords, OAuth data, and full Telegram chat IDs.

Verification:
- Friendly Phase 7E recall test passed without raw labels.
- Friendly reminder-failure search test passed without raw paths.
- Latest backup `/btw` test passed.
- Risky action block test passed.
- Raw mode still returns technical output.
- Reminder update, recurring, create, delivery, quick healthcheck, and deep healthcheck passed.

No private route activated.
No default model changed.
No reminder system changes.
