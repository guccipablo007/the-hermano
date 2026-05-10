# Phase 6K: Router Executor Wrapper

Created:
/root/.hermes/scripts/hermes_router_execute.py

Purpose:
Make Telegram router execution deterministic.

Why:
Telegram Hermes could call hermes_model_call.py, but did not reliably save output files or run verification.

Supported mode:

* coder_file

No Hermes default model changed.
Private route remains inactive.
