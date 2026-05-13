# Phase 7I-D: NewCoin Popular Model Routing

Goal:
Replace Doubao as the selected coding route with verified popular NewCoin routing models, while keeping NewCoin primary and OpenRouter fallback-only.

Investigation:
- Queried NewCoin `/models` using the configured NewCoin endpoint without printing secrets.
- Verified candidate IDs existed for Gemini, Kimi, DeepSeek, MiniMax, GLM, and Qwen.
- Tested candidate models with short exact-output prompts.

Results:
- `gemini-2.5-flash` exists but failed repeat exact-output verification by returning an incomplete marker, so it was not selected as default.
- `qwen3-32b` passed and remains the verified stable default/general/simple model.
- `kimi-k2-thinking` exists but returned an endpoint error during test; `kimi-k2.6` passed and was selected for reasoning/agentic routing.
- `deepseek-v3.2` passed and was selected for coding/debugging routing.
- Doubao was removed from the primary coding route.
- GPT/OpenAI NewCoin models remain avoided as defaults because they may be expensive.

Final routing:
- Default/general/simple: `qwen3-32b`
- Reasoning/agentic: `kimi-k2.6`
- Coding/debugging: `deepseek-v3.2`
- OpenRouter: fallback only

Future planning only:
- `/nc` may later force NewCoin for a request.
- Future optional hints may include `/nc code`, `/nc reason`, or `/nc cheap`.
- `/nc` was not implemented in this phase.

Verification:
- Provider status script created/updated and tested.
- `/btw` provider/model status now uses storage-backed provider status.
- Reminder update, recurring reminder, one-shot create, and one-shot delivery regressions passed.
- Quick/deep healthchecks passed.
- Gateway restarted and startup quick healthcheck passed.

Protected:
- No Gmail/YouTube configuration changed.
- No private_data route activated.
- Reminder logic unchanged.
- No provider keys or auth headers printed.
