# Phase 6C: Manual Model Call Helper

Created:
/root/.hermes/scripts/hermes_model_call.py

Purpose:
Manual testing of decentralized worker routes before activating routing in Telegram.

Tested routes:
- basic: passed
- coder: provider returned 401 for qwen3-coder-plus
- complex_reasoning: passed
- vision text-only smoke test: provider returned 503 for qwen3-vl-plus availability
- source_verified_research: passed
- private_data: refused as expected

No Hermes default model changed.
No gateway restart performed.
No Telegram routing activated.
