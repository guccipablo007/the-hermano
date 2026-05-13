# Phase 7I-F: Live Natural-Language Model Router

Goal:
Enforce natural-language intent routing in live Telegram before generic model response. Slash commands remain optional shortcuts, not the primary routing mechanism.

Changes:
- Patched `/root/.hermes/scripts/hermes_model_router.py` to prioritize natural provider/model status, reminder lookup, Hermes failure/history recall, coding/debugging, reasoning/architecture, and default/simple routes.
- Added `/root/.hermes/scripts/hermes_live_natural_router.py` as the live Telegram router bridge with sanitized route audit logging.
- Patched `/usr/local/lib/hermes-agent/gateway/run.py` so Telegram messages first pass through the live router.
- Tool-first routes return direct verified answers for provider status, reminder lookup/listing, `/btw` side questions, and session recall/history questions.
- Non-tool model routes inject per-turn model context and use the selected NewCoin model without changing persistent default config.

Routing:
- Provider/model status: verified provider-status tool.
- Reminder questions: storage-backed reminder lookup tool.
- Hermes failure/history questions: local session recall/rebuild notes first.
- Coding/debugging/app/Firebase/database: NewCoin `deepseek-v3.2`.
- Reasoning/architecture/root-cause analysis: NewCoin `kimi-k2.6`.
- Default/simple chat/writing/translation: NewCoin `qwen3-32b`.
- OpenRouter remains fallback only.

Verification:
- Python syntax checks passed for changed files.
- Natural provider/model, root-cause recall, Firebase/debugging, reasoning, `/btw`, and reminder-list router tests passed locally.
- Reminder update, recurring reminder, one-shot create, and one-shot delivery regressions passed.
- Quick and deep Ops Guardian healthchecks passed.

Safety:
- No provider keys, auth headers, Telegram bot token, OAuth tokens, passwords, or full Telegram chat IDs are printed.
- Route audit logs store sanitized intent snippets only.
- Reminder logic was not changed.
- `/btw` behavior was preserved.
- No 4-agent delegation framework was implemented.
