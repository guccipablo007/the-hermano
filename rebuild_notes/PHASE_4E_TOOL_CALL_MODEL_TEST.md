# Phase 4E: Tool Calling Model Test

Purpose:
Telegram was narrating command JSON instead of executing tools.

Action:
Tested whether the configured OpenRouter model emits real structured tool_calls.
If needed, switched Hermes main model to the first tested model that returns actual tool_calls.

Rule preserved:
No hardcoded natural-language phrase routers.
