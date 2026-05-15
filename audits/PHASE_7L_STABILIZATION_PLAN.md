# Phase 7L Stabilization Plan

## Executive Verdict

Hermes is recoverable.

Hermes is not irreparably broken, but it is currently architecture-drifted:

- multiple route owners
- mixed script repo and dirty gateway repo sources of truth
- verified tool routes living beside raw model routes
- direct responses bypassing the shared final sanitizer
- session-context heuristics being used as routing state

## Ranked Stabilization Recommendations

### 1. Must fix immediately

1. Pick one first owner for each message family.
   - reminders
   - artifacts
   - `/btw`
   - news
   - delegated status / risky-action blocking
2. Stop maintaining two active reminder lookup implementations.
3. Ensure every direct-response path passes through one shared final text sanitization layer, even if the response came from a tool-first early return.
4. Freeze the current gateway routing order into one documented contract before further behavior changes.
5. Audit the factual Q&A raw model path before adding more feature patches.

### 2. Should simplify

1. Collapse reminder ownership to:
   - one inquiry guard / lookup owner
   - one create/update owner
2. Collapse artifact ownership to:
   - one detection owner
   - one verification/delivery owner
3. Remove duplicate `/btw` interception.
4. Keep the live natural router as a classifier only, or keep it as the sole direct-response owner, but not both alongside older gateway pre-routers.
5. Separate routing from execution from rendering from delivery in the audit trace design.

### 3. Can remove or deprecate

1. Legacy gateway reminder lookup pre-router once storage-backed lookup is the single reminder-read owner.
2. `hermes_reminder_lookup.py` once its remaining lookup use cases are either migrated or explicitly retired.
3. Legacy gateway `/btw` pre-router if the live natural router remains the canonical `/btw` owner.
4. Legacy artifact pre-router if artifact detection and execution stay inside the live natural router.
5. Any stale skill text that still describes superseded routing paths.

### 4. Should keep

1. `hermes_prechange_backup`
2. `hermes_verified_news.py`
3. `hermes_storage_backed_lookup.py`
4. `hermes_reminder_intent_guard.py`
5. `hermes_agent_delegate.py` read-only status and risky-action block policy
6. `_sanitize_user_visible_response(...)` as a concept, after it is moved into a single universal final-delivery layer
7. `hermes_telegram_deliver.py` Telegram file delivery verification pattern

### 5. Needs live test before any refactor

1. Output loop / repeated-send behavior
2. Direct-response sanitizer coverage
3. PDF after a new unrelated factual question
4. `/btw` after live natural router changes
5. Reminder inquiry vs create ambiguity
6. Delegated status output after ledger pruning or schema changes
7. News direct URL quality and ranking

## Direct Answers

### Is Hermes irreparably broken?

No. Hermes is recoverable.

### Which patch created the most routing complexity?

`PHASE_7IF_LIVE_NATURAL_LANGUAGE_ROUTER` created the most routing complexity.

Reason:

- it inserted a new Telegram-first owner in `gateway/run.py`
- it also introduced a second use of the same router later in the flow for model override
- it did this without removing older `/btw`, reminder-lookup, and artifact pre-routers

That created stacked routing rather than replacement routing.

### Which scripts are dead or duplicate?

Dead: none can be proven fully dead from the live audit.

Duplicate or shadowed:

- `/root/.hermes/scripts/hermes_reminder_lookup.py`
  - still used by legacy gateway reminder pre-router
  - duplicated by `/root/.hermes/scripts/hermes_storage_backed_lookup.py`
- `/root/.hermes/scripts/telegram_artifact_prerouter.py`
  - still active in `run.py`
  - shadowed for common PDF/resend requests by `hermes_live_natural_router.py`
- `/root/.hermes/scripts/hermes_btw_handler.py`
  - correct owner for `/btw` behavior
  - but invoked both by the live natural router and the legacy gateway `/btw` pre-router

### Which message path still allows raw model hallucination?

The generic non-tool path:

- `gateway/run.py`
- `hermes_live_natural_router.handle(...)` returns `direct_response=false`
- second router pass sets `route_model_override`
- `_run_agent(...)` answers with a model

This currently owns factual Q&A such as:

- `Who made the first ever electric car?`
- `Who made the first ever electric airplane?`

It also remains part of reminder-create flow after the reminder guard validates the request.

### Which route should own factual Q&A?

Recommended ownership:

- timeless low-risk factual Q&A: one generic factual answer route after classification, not artifact or delegation logic
- latest or source-sensitive factual Q&A: verified tool route, not raw model route

Current problem:

- the system does not clearly separate those two classes

### Which route should own PDF/artifacts?

One owner should detect artifact intent.

One owner should verify and deliver artifacts.

Recommended stable ownership:

- detection: artifact-specific pre-router
- verification/delivery: `hermes_file_delivery_verify.py` for simple verified PDF/resend flows
- rich multi-format generation: `hermes_rich_output_execute.py` and related deterministic builders

The live natural router should not also be a parallel artifact owner if the gateway artifact pre-router remains active.

### Which route should own reminders?

Recommended stable ownership:

- reminder inquiry and upload schedule:
  - one storage-backed read owner
- reminder create/update:
  - reminder guard plus verified cronjob storage/delivery path

The raw model route should not own reminder behavior.

### Which route should own news?

`hermes_verified_news.py`

### Which route should own agent delegation?

`hermes_agent_delegate.py`

The live natural router should classify when to use it, but the delegation logic, ledger, status, and safety policy should stay in the delegate layer.

### What is the minimal stable core?

Recommended minimal stable core:

1. `gateway/run.py` with one documented Telegram pre-routing stage only
2. `hermes_live_natural_router.py` as classifier and direct-response owner only if older competing pre-routers are removed
3. `hermes_model_router.py` as pure route classifier
4. `hermes_reminder_intent_guard.py`
5. one reminder read path
   - preferably `hermes_storage_backed_lookup.py`
6. one news path
   - `hermes_verified_news.py`
7. one artifact verification/delivery path
   - `hermes_file_delivery_verify.py`
   - `hermes_telegram_deliver.py`
8. one delegation/safety path
   - `hermes_agent_delegate.py`
9. one final output sanitizer applied to every user-visible text response

## Biggest Risks

1. Live gateway repo drift outside the backup mirror
2. Duplicated route ownership in `run.py`
3. Raw factual model path without verification
4. Direct-response text bypassing shared final sanitization
5. Artifact context inferred from transcript history instead of explicit binding

## Recommended Reset Strategy

1. Freeze current architecture and do not add features until ownership is simplified.
2. Decide whether the live natural router replaces or merely advises the older gateway pre-routers.
3. Remove duplicate ownership one message family at a time.
4. Add trace logging only after ownership is clear enough that traces describe one route, not several competing partial routes.
5. After ownership is simplified, run the Phase 7L basic task suite before any new feature patch.
