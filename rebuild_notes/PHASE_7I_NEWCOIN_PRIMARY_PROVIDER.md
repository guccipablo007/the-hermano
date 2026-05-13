# Phase 7I: NewCoin Primary Provider

Goal:
Make NewCoin the primary Hermes provider for normal Telegram intelligence, reasoning, coding help, reminders, /btw, and general assistant work while keeping OpenRouter as fallback only.

Changes:
- Added/updated `providers.newcoin` in `/root/.hermes/config.yaml` using supported custom provider syntax.
- Set `model.provider` to `custom:newcoin`.
- Set default model to `qwen3-32b` after model-list and chat-completion verification.
- Kept OpenRouter models as fallback providers only.
- Synced NewCoin env variable names into Hermes-managed `.env` without printing secrets.
- Updated safe routing policy metadata to reflect NewCoin primary / OpenRouter fallback.

Verified:
- NewCoin `/models` availability returned image/chat model inventory.
- NewCoin chat completion returned `NEWCOIN_PROVIDER_TEST=PASSED`.
- `/btw` regression passed.
- Reminder update, recurring, one-shot create, and one-shot delivery regressions passed.
- Quick and deep healthchecks passed before restart.
- Gateway restarted and remained active.

Protected:
- No Gmail/YouTube configuration changed.
- No private_data route activated.
- Reminder logic unchanged.
- No provider keys printed.
