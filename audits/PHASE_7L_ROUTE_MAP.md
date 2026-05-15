# Phase 7L Route Map

This map records the current live route on the VPS as observed in:

- `/usr/local/lib/hermes-agent/gateway/run.py`
- `/root/.hermes/scripts/hermes_live_natural_router.py`
- `/root/.hermes/scripts/hermes_model_router.py`
- related live tool scripts

## Global entry path

Telegram text messages currently enter through:

1. `gateway/run.py` early live natural-language router bridge
2. legacy gateway `/btw` pre-router
3. legacy gateway reminder lookup pre-router
4. legacy gateway artifact pre-router
5. `_prepare_inbound_message_text`
6. second live natural router pass for per-turn model override
7. `_run_agent(...)`
8. `_sanitize_user_visible_response(...)` for non-direct model replies only
9. `gateway/platforms/telegram.py::TelegramAdapter.send(...)`

Direct responses from step 1 skip steps 2-8.

## 1. `Any reminders?`

- Entrypoint: `/usr/local/lib/hermes-agent/gateway/run.py` live natural router bridge
- First router decision: `hermes_live_natural_router.handle(...)` -> direct response
- Model selected: `qwen3-32b`
- Tool selected: `hermes_agent_delegate_execute_readonly`
- Agent selected: `Personal/Admin & Tutor Agent`
- Fallback path: if live natural router fails, gateway sends `NOT VERIFIED`; legacy reminder lookup pre-router does not clearly own this exact phrasing
- Output sanitizer path: script-level masking only; gateway final sanitizer is bypassed
- Telegram delivery/chunking path: `TelegramAdapter.send(...)`
- Evidence required: `hermes_storage_backed_lookup.py any-reminders --format friendly` output via delegate read-only path
- Known failure risk: duplicate reminder ownership remains in the system; older ledger contains one failed reminder-read entry before a later verified one

## 2. `What's my upload schedule?`

- Entrypoint: `/usr/local/lib/hermes-agent/gateway/run.py` live natural router bridge
- First router decision: direct response
- Model selected: `qwen3-32b`
- Tool selected: `hermes_agent_delegate_execute_readonly`
- Agent selected: `Personal/Admin & Tutor Agent`
- Fallback path: if live natural router fails, message risks falling toward generic handling because the legacy reminder pre-router is not the canonical owner
- Output sanitizer path: script-level masking only
- Telegram delivery/chunking path: `TelegramAdapter.send(...)`
- Evidence required: `hermes_storage_backed_lookup.py upload-schedule --format friendly`
- Known failure risk: two reminder lookup stacks exist; only one is storage-backed canonical in current policy

## 3. `Remind me tomorrow at 8 AM to call Mr Wang`

- Entrypoint: `/usr/local/lib/hermes-agent/gateway/run.py` live natural router bridge
- First router decision: `hermes_live_natural_router.handle(...)` -> reminder guard validates create intent, then returns `direct_response=false`
- Model selected: per-turn override `qwen3-32b`
- Tool selected: none at pre-router stage
- Agent selected: none at pre-router stage; falls into generic main-agent execution
- Fallback path: generic agent path with model override; downstream reminder creation can still call cronjob tooling if the model chooses it
- Output sanitizer path: gateway `_sanitize_user_visible_response(...)` after `_run_agent(...)`
- Telegram delivery/chunking path: `TelegramAdapter.send(...)`
- Evidence required: reminder creation success should be proven by cron storage verification and delivery evidence, but that proof is not enforced by the route itself before agent execution
- Known failure risk: this remains a raw model path after guard validation; it is the clearest reminder route that can still drift into model-led behavior

## 4. `Who made the first ever electric car?`

- Entrypoint: `/usr/local/lib/hermes-agent/gateway/run.py` live natural router bridge
- First router decision: `default/simple`, `direct_response=false`
- Model selected: per-turn override `qwen3-32b`
- Tool selected: none
- Agent selected: none
- Fallback path: generic agent fallback stack inside main model execution
- Output sanitizer path: gateway `_sanitize_user_visible_response(...)`
- Telegram delivery/chunking path: `TelegramAdapter.send(...)`
- Evidence required: none required by route
- Known failure risk: raw factual model answer path; no verification tool is required

## 5. `Who made the first ever electric airplane?`

- Entrypoint: `/usr/local/lib/hermes-agent/gateway/run.py` live natural router bridge
- First router decision: `default/simple`, `direct_response=false`
- Model selected: per-turn override `qwen3-32b`
- Tool selected: none
- Agent selected: none
- Fallback path: generic agent fallback stack
- Output sanitizer path: gateway `_sanitize_user_visible_response(...)`
- Telegram delivery/chunking path: `TelegramAdapter.send(...)`
- Evidence required: none required by route
- Known failure risk: same raw factual model path as message 4; current system does not distinguish uncertain historical claims from safe small-talk

## 6. `PDF`

- Entrypoint: `/usr/local/lib/hermes-agent/gateway/run.py` live natural router bridge
- First router decision: direct response via `hermes_file_delivery_verify`
- Model selected: `qwen3-32b`
- Tool selected: `hermes_file_delivery_verify`
- Agent selected: none
- Fallback path: if the live natural router did not intercept, legacy `telegram_artifact_prerouter.py` could handle it, but in current live flow it is shadowed
- Output sanitizer path: script-level masking only; gateway final sanitizer is bypassed
- Telegram delivery/chunking path:
  - text reply through `TelegramAdapter.send(...)`
  - file delivery through `/root/.hermes/scripts/hermes_telegram_deliver.py` direct Bot API `sendDocument`
- Evidence required:
  - session transcript context
  - file exists
  - file size > 0
  - PDF header valid
  - extracted text contains required topic terms
  - artifact registry write
  - Telegram API `ok=true`
- Known failure risk: topic is resolved from the latest non-artifact session context, so `PDF` alone can bind to the wrong subject

## 7. `Show me the file here in Telegram`

- Entrypoint: `/usr/local/lib/hermes-agent/gateway/run.py` live natural router bridge
- First router decision: direct response via `hermes_file_delivery_verify`
- Model selected: `qwen3-32b`
- Tool selected: `hermes_file_delivery_verify`
- Agent selected: none
- Fallback path: legacy artifact pre-router exists but is normally shadowed
- Output sanitizer path: script-level masking only
- Telegram delivery/chunking path:
  - text response through `TelegramAdapter.send(...)`
  - file resend through `hermes_telegram_deliver.py`
- Evidence required:
  - latest verified artifact in `/root/.hermes/artifacts/latest_artifacts.jsonl`
  - same masked chat target
  - file still exists and verifies
  - Telegram API `ok=true`
- Known failure risk: resend owner is correct now, but it still depends on registry freshness and the latest-verified-artifact heuristic

## 8. `Use your web skills to give me top international politics news, top 5 AI news and top 5 Premier League news`

- Entrypoint: `/usr/local/lib/hermes-agent/gateway/run.py` live natural router bridge
- First router decision: direct response
- Model selected: `qwen3-32b`
- Tool selected: `hermes_verified_news`
- Agent selected: none
- Fallback path: if the live natural router failed, there is no equally strong legacy owner; generic model behavior would be unsafe
- Output sanitizer path: script-level formatting only; gateway final sanitizer is bypassed
- Telegram delivery/chunking path: `TelegramAdapter.send(...)`, chunked if needed
- Evidence required: verified article set with `source`, `title`, `published_at`, `url`
- Known failure risk: direct URLs are not always resolved beyond Google News RSS links; ranking quality is better but still heuristic

## 9. `What model are you using?`

- Entrypoint: `/usr/local/lib/hermes-agent/gateway/run.py` live natural router bridge
- First router decision: direct response
- Model selected: `qwen3-32b`
- Tool selected: `hermes_provider_status`
- Agent selected: none
- Fallback path: if the live natural router failed, `hermes_model_router.py` still classifies it tool-first, but that second pass only affects model override on the generic path
- Output sanitizer path: script-level formatting only
- Telegram delivery/chunking path: `TelegramAdapter.send(...)`
- Evidence required: provider status script output
- Known failure risk: minimal; this is a stable tool-first path

## 10. `/btw what provider are you using now?`

- Entrypoint: `/usr/local/lib/hermes-agent/gateway/run.py` live natural router bridge
- First router decision: direct response via `hermes_btw_handler`
- Model selected: `qwen3-32b`
- Tool selected: `hermes_btw_handler`
- Agent selected: none
- Fallback path: legacy gateway `/btw` pre-router exists and calls the same handler if the live natural router does not already return
- Output sanitizer path: script-level formatting only
- Telegram delivery/chunking path: `TelegramAdapter.send(...)`
- Evidence required: provider status tool output from inside `/btw` handling
- Known failure risk: duplicate ownership between live natural router and legacy `/btw` pre-router

## 11. `Show recent delegated tasks`

- Entrypoint: `/usr/local/lib/hermes-agent/gateway/run.py` live natural router bridge
- First router decision: direct response
- Model selected: `qwen3-32b`
- Tool selected: `hermes_agent_delegate_status`
- Agent selected: `Hermes Overseer / Main Agent` for status rendering
- Fallback path: if live natural router failed, message would likely fall through to generic chat because there is no separate gateway pre-router for it
- Output sanitizer path: script-level formatting only
- Telegram delivery/chunking path: `TelegramAdapter.send(...)`
- Evidence required: `/root/.hermes/agent_tasks/tasks.jsonl` and report files
- Known failure risk: output is friendly, but historical failed rows remain mixed with current successful behavior

## 12. `Fix Firebase app now`

- Entrypoint: `/usr/local/lib/hermes-agent/gateway/run.py` live natural router bridge
- First router decision: direct blocked response
- Model selected: `qwen3-32b` in the response wrapper, but upstream classification recognizes coding/debugging intent
- Tool selected: `hermes_agent_delegate_blocked_risky`
- Agent selected: logical specialist is `Apps, Coding & Complex Builds Agent` in delegate classification
- Fallback path: user can request a dry-run plan; current live route does not execute
- Output sanitizer path: script-level text only
- Telegram delivery/chunking path: `TelegramAdapter.send(...)`
- Evidence required: none to block; execution evidence would be required only if a safe dry-run or future approved execution path is used
- Known failure risk: phrases that are less explicit than `fix ... now` may still fall into the generic coding model route instead of the explicit block path

## 13. `Restart Hermes gateway`

- Entrypoint: `/usr/local/lib/hermes-agent/gateway/run.py` live natural router bridge
- First router decision: direct blocked response
- Model selected: `qwen3-32b` in the wrapper response, but delegate classification marks it as Ops/Verification-related
- Tool selected: `hermes_agent_delegate_blocked_risky`
- Agent selected: logical specialist is `Ops & Verification Agent` in delegate classification
- Fallback path: user can request a dry-run plan; live direct execution remains blocked
- Output sanitizer path: script-level text only
- Telegram delivery/chunking path: `TelegramAdapter.send(...)`
- Evidence required: none to block; verified restart would require service evidence if ever allowed
- Known failure risk: none on the current block path, but restart intent also appears inside other health/admin flows, so ownership should stay singular

## Route Ownership Summary

- Reminders: currently split between live natural router, reminder guard, legacy reminder lookup pre-router, `hermes_storage_backed_lookup.py`, and `hermes_reminder_lookup.py`
- Factual Q&A: currently generic model path
- News: currently `hermes_verified_news.py`
- Artifacts: currently live natural router plus `hermes_file_delivery_verify.py`, with legacy artifact pre-router still present
- `/btw`: currently live natural router first, legacy `/btw` pre-router second
- Delegated status and risky action blocking: currently live natural router plus `hermes_agent_delegate.py`
