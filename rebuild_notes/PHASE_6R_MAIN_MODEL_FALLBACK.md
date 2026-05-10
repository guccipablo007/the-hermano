# Phase 6R: Main Model Fallback

Problem:
Telegram natural PDF request failed after tool results because the main model returned empty content and no fallback provider was configured.

Fix:
Added OpenRouter fallback providers to model.fallback_providers:
- openai/gpt-oss-120b
- qwen/qwen3-coder

No NewCoin routing changed.
No private_data route activated.
No Gmail/YouTube configuration changed.
