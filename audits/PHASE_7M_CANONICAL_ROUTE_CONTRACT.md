# Phase 7M Canonical Route Contract

Date: 2026-05-15
Scope: live Telegram routing ownership and universal final text sanitization

## Contract

Telegram text now follows one canonical gateway contract:

1. Receive Telegram text in `/usr/local/lib/hermes-agent/gateway/run.py`
2. Prepare inbound text once
3. Call `/root/.hermes/scripts/hermes_live_natural_router.py` once as the canonical first owner
4. If the router returns a direct response, pass that text through the shared final sanitizer and deliver it through the gateway adapter send path
5. If the router does not return a direct response, use the router decision as the model-route override
6. Run the normal model path
7. Pass the model output through the same shared final sanitizer
8. Deliver the final text through the gateway adapter send path

## Final Sanitizer Path

Shared functions in `gateway/run.py`:

- `_sanitize_user_visible_response(...)`
- `_sanitize_and_deliver_text(...)`

The shared sanitizer applies to:

- direct tool replies
- `/btw` replies routed through the canonical router
- storage-backed reminder lookup replies
- artifact/PDF status text
- verified news text
- delegated task status text
- model replies
- queued follow-up first-response delivery

The sanitizer removes or masks:

- full Telegram chat IDs
- bot tokens, bearer tokens, and API keys
- raw tool-call syntax
- raw cronjob JSON / tool JSON leakage
- internal self-correction / thought-process scaffolding
- obvious repeated-output loops
- raw debug markers unless explicitly requested

## Owner Map

Canonical first owner:

- `/root/.hermes/scripts/hermes_live_natural_router.py`

Owners invoked through the canonical router:

- Reminders read path: `/root/.hermes/scripts/hermes_storage_backed_lookup.py`
- Reminder intent validation: `/root/.hermes/scripts/hermes_reminder_intent_guard.py`
- News: `/root/.hermes/scripts/hermes_verified_news.py`
- Artifacts/PDF/resend: `/root/.hermes/scripts/hermes_file_delivery_verify.py`
- `/btw`: `/root/.hermes/scripts/hermes_btw_handler.py`
- Delegated status / risky-action blocks / read-only / low-risk write gates: `/root/.hermes/scripts/hermes_agent_delegate.py`

Still not changed in this phase:

- Factual Q&A ownership remains on the existing model path after canonical routing
- Provider/model routing remains unchanged
- Destructive-action blocks remain unchanged

## Legacy Pre-Routers

These remain on disk for rollback/reference only and are no longer active as separate Telegram interceptors in `gateway/run.py`:

- legacy `/btw` pre-router
- legacy reminder lookup pre-router
- legacy artifact pre-router

Legacy scripts retained:

- `/root/.hermes/scripts/hermes_reminder_lookup.py`
- `/root/.hermes/scripts/telegram_artifact_prerouter.py`

They are now documented as legacy/fallback components, not canonical entry owners.
