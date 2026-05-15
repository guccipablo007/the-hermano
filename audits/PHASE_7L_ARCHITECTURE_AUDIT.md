# Phase 7L Architecture Audit

## Scope

This audit was produced from the live Hermes VPS on 2026-05-15 over SSH port 9123.

Runtime behavior was not patched in this phase. The only intended Phase 7L outputs are audit documents under:

- `/root/.hermes/audits/PHASE_7L_ARCHITECTURE_AUDIT.md`
- `/root/.hermes/audits/PHASE_7L_CHANGE_INVENTORY.json`
- `/root/.hermes/audits/PHASE_7L_ROUTE_MAP.md`
- `/root/.hermes/audits/PHASE_7L_STABILIZATION_PLAN.md`
- `/root/.hermes/audits/PHASE_7L_BASIC_TASK_TEST_SUITE.md`

## Evidence Sources

- Live backup mirror repo: `/root/hermano-backup`
- Live gateway repo: `/usr/local/lib/hermes-agent`
- Live Hermes tree: `/root/.hermes`
- Gateway entrypoint: `/usr/local/lib/hermes-agent/gateway/run.py`
- Telegram adapter: `/usr/local/lib/hermes-agent/gateway/platforms/telegram.py`
- Route and gate scripts:
  - `/root/.hermes/scripts/hermes_live_natural_router.py`
  - `/root/.hermes/scripts/hermes_model_router.py`
  - `/root/.hermes/scripts/hermes_reminder_intent_guard.py`
  - `/root/.hermes/scripts/telegram_artifact_prerouter.py`
  - `/root/.hermes/scripts/hermes_storage_backed_lookup.py`
  - `/root/.hermes/scripts/hermes_reminder_lookup.py`
  - `/root/.hermes/scripts/hermes_verified_news.py`
  - `/root/.hermes/scripts/hermes_file_delivery_verify.py`
  - `/root/.hermes/scripts/hermes_agent_delegate.py`
  - `/root/.hermes/scripts/hermes_btw_handler.py`
- Live session evidence:
  - `/root/.hermes/sessions/sessions.json`
  - `/root/.hermes/sessions/<session>.jsonl`
- Live artifact and task evidence:
  - `/root/.hermes/artifacts/latest_artifacts.jsonl`
  - `/root/.hermes/agent_tasks/tasks.jsonl`

## Repo and Runtime State

### 1. Backup mirror repo

- Repo root: `/root/hermano-backup`
- Purpose: safe mirrored backup repo used by `hermes_prechange_backup`
- Current branch: `main`
- Current state during audit collection: clean
- Recent commits are timestamped safe-backup commits, not semantic phase commits

### 2. Gateway runtime repo

- Repo root: `/usr/local/lib/hermes-agent`
- Current state during audit collection: dirty and behind `origin/main` by 102 commits
- Local live modifications were present in:
  - `gateway/run.py`
  - `tools/cronjob_tools.py`
  - `cron/scheduler.py`
  - `cron/jobs.py`
- This matters because Hermes runtime behavior depends on both `/root/.hermes` scripts and uncommitted gateway/cron edits outside the backup mirror

### 3. Current routing shape

Hermes does not have one route owner. It has a layered stack:

1. Telegram adapter receives user message.
2. `gateway/run.py` executes an early live natural-language router bridge.
3. If the live router returns a direct response, the message is sent immediately and the rest of the gateway pipeline is skipped.
4. If not, `run.py` still contains older Telegram pre-routers for:
   - `/btw`
   - reminder lookup
   - artifact requests
5. If those do not return early, the gateway prepares message text and runs the live natural router a second time only to pick a per-turn model override.
6. The main agent runs with the selected model override.
7. The final model response is sanitized by `_sanitize_user_visible_response`.
8. TelegramAdapter sends the final text response, chunking when needed.

This means the current live system contains both:

- direct tool-first response paths
- raw model answer paths
- legacy gateway pre-routers that remain after newer router logic was added

## Current Telegram Execution Order

Observed in `/usr/local/lib/hermes-agent/gateway/run.py`:

1. Live natural-language router pre-router
   - Calls `/root/.hermes/scripts/hermes_live_natural_router.py`
   - If `direct_response=true`, sends text immediately and returns
2. Legacy `/btw` pre-router
   - Calls `hermes_btw_handler.handle`
3. Legacy reminder lookup pre-router
   - Calls `/root/.hermes/scripts/hermes_reminder_lookup.py`
4. Legacy artifact pre-router
   - Calls `/root/.hermes/scripts/telegram_artifact_prerouter.py`
5. Message preparation
6. Live natural router again for per-turn model override
7. `_run_agent(...)`
8. `_sanitize_user_visible_response(...)`
9. `TelegramAdapter.send(...)`

## Key Architectural Findings

### A. The live natural router became the de facto first owner

`hermes_live_natural_router.py` now decides many message classes before older dedicated gateway pre-routers run:

- reminders
- upload schedule
- `/btw`
- news
- delegated-task status
- risky delegated actions
- PDF/file requests

This makes older gateway pre-routers partially redundant, but they are still active in `run.py`.

### B. Several message classes have overlapping owners

Observed overlaps:

- `/btw`
  - live natural router can route to `hermes_btw_handler`
  - legacy `/btw` pre-router can also route to `hermes_btw_handler`
- reminder lookup
  - live natural router uses `hermes_storage_backed_lookup.py`
  - legacy gateway reminder pre-router still uses `hermes_reminder_lookup.py`
- artifact delivery
  - live natural router routes `PDF` and resend phrases to `hermes_file_delivery_verify.py`
  - legacy gateway artifact pre-router still exists and can handle similar requests

### C. Direct-response paths bypass the gateway response sanitizer

When the live natural router returns `direct_response=true`, `run.py` sends that text immediately. The later gateway sanitizer is not applied to that text.

This means direct-response scripts must sanitize themselves correctly. Some do. The architecture does not enforce one common post-tool output sanitizer for all direct responses.

### D. Factual Q&A still falls through to raw model answers

Examples:

- `Who made the first ever electric car?`
- `Who made the first ever electric airplane?`

These currently route to:

- live natural router -> `default/simple`
- second live router pass -> per-turn model override `qwen3-32b`
- generic main agent path

No factual verification tool is required on that path.

### E. The PDF path depends on latest session context, not explicit message-topic binding

`hermes_file_delivery_verify.py` now builds a PDF from the latest non-artifact topic found in the session transcript. That improves over placeholder PDFs, but it also creates a coupling:

- `PDF` alone does not carry its own topic
- the tool resolves topic by scanning the current session transcript
- if the most recent non-artifact topic changed, `PDF` may bind to the wrong subject

This was directly visible during the audit:

- the latest transcript topic changed from electric car to electric airplane
- later `PDF` requests resolved to the airplane topic

This is useful for continuity but fragile as an architectural ownership rule.

### F. Gateway repo drift is not fully mirrored by the script-level audit story

The live runtime also depends on uncommitted gateway and cron changes outside `/root/.hermes`:

- `gateway/run.py`
- `cron/jobs.py`
- `cron/scheduler.py`
- `tools/cronjob_tools.py`

Those changes are large and materially affect routing and reminder delivery verification. The system is therefore not represented by a single clean git-tracked source of truth.

### G. Stale ledger evidence remains visible after behavior changed

`/root/.hermes/agent_tasks/tasks.jsonl` still contains older blocked artifact-write entries such as:

- blocked multi-step artifact requests
- blocked resend requests

The current live behavior is better than those historical ledger rows, but the ledger still shows prior routing failures. This is useful evidence, but it also means operator status views may mix current behavior with stale incidents.

## Overlapping Routers and Gates

| Component | What it handles now | What it should not handle | Can block execution | Can call tools/scripts | Can emit user-facing text | Logs evidence | Main conflict risk |
|---|---|---|---|---|---|---|---|
| `gateway/run.py` live natural router bridge | All Telegram text before other pre-routers | Anything already owned by simpler legacy pre-router, if those remain active | Yes, by returning early | Yes, via `hermes_live_natural_router.py` subprocess | Yes | Route audit file indirectly | Shadows later pre-routers |
| `hermes_live_natural_router.py` | Provider status, reminders, news, artifacts, delegated status, risky action blocking, route preview | Low-level artifact generation details, duplicate `/btw` ownership, duplicate reminder lookup ownership | Yes | Yes | Yes | `live_route_audit.jsonl` | Became a second dispatcher plus tool caller |
| `hermes_model_router.py` | Tool-vs-default-vs-reasoning-vs-coding classification | Final user-facing delivery decisions | No directly | No | Only friendly classification output | No durable evidence by itself | Duplicates logic with live natural router regexes |
| `hermes_reminder_intent_guard.py` | Ambiguous reminder create/inquiry validation | Reminder lookup formatting, cron delivery | Yes | No | Yes | No durable ledger by itself | Sits beside two reminder lookup systems |
| legacy reminder pre-router in `run.py` | Reminder lookup via `hermes_reminder_lookup.py` | Anything now owned by storage-backed lookup route | Yes | Yes | Yes | No dedicated audit file | Duplicates storage-backed reminder lookup route |
| `hermes_storage_backed_lookup.py` | Upload schedule, reminder list | Natural-language parsing beyond its narrow commands | Yes, by returning NOT VERIFIED | No external tools | Yes | Tool output only | Duplicates `hermes_reminder_lookup.py` list role |
| `hermes_reminder_lookup.py` | Legacy list/search/next/status reminder lookup | Storage-backed-only policy if that is the canonical rule | Yes | No | Yes | Tool output only | Legacy pre-router still calls it |
| `telegram_artifact_prerouter.py` | Artifact-like natural requests | Requests already fully owned by `hermes_live_natural_router.py` | Yes | Yes | Yes | No durable audit file | Shadowed by live natural router for PDF/resend |
| `hermes_file_delivery_verify.py` | PDF create/resend verification and Telegram file delivery | General factual Q&A ownership | Yes | Yes | Yes | Artifact registry | Topic inference depends on session context |
| `hermes_verified_news.py` | Verified news retrieval | General factual Q&A outside news | Yes | Yes | Yes | Tool output only | Direct-response path bypasses gateway sanitizer |
| `hermes_btw_handler.py` | Read-only side questions | Non-side workflow messages | Yes | Yes | Yes | Local recall evidence only | Duplicated by live natural router plus gateway `/btw` pre-router |
| `hermes_agent_delegate.py` | Delegation classify, status, read-only execution, low-risk write gate | Generic chat, direct factual Q&A | Yes | Yes | Yes | `tasks.jsonl` and report files | Used both as governance layer and user-facing response source |
| gateway `_sanitize_user_visible_response` | Final non-direct model responses | Direct-response tool outputs | No | No | No | No | Not applied to early-return tool responses |
| `TelegramAdapter.send` | Final text delivery and chunking | Route ownership | No | No | No | Telegram message IDs only | Multiple send origins can still create repeated delivery if upstream emits repeatedly |

## Main Failure Modes Observed or Strongly Implied

1. Route duplication creates split ownership.
2. Default factual Q&A still allows raw model answers without verification.
3. Direct-response paths are not forced through one shared sanitizer.
4. Artifact topic selection depends on latest session context rather than an explicit bound artifact request.
5. The gateway runtime repo is locally modified and behind upstream, so live behavior is not reducible to the backup mirror alone.
6. Reminder lookup has two active implementations with different ownership points.
7. Operator evidence stores are separate:
   - route audit
   - delegated task ledger
   - artifact registry
   - sessions transcript
   - reminder storage
   They are useful, but not stitched into one trace.

## Proposed Trace Schema

Do not implement in Phase 7L. This is a design only.

Recommended location:

- `/root/.hermes/traces/live_message_traces.jsonl`

Recommended JSON record:

```json
{
  "trace_id": "20260515T153000Z-<short-id>",
  "timestamp": "2026-05-15T15:30:00Z",
  "incoming_message_preview": "Show me the file here in Telegram",
  "chat_id_masked": "<chat_id_masked>",
  "route_decision": "tool",
  "router_component": "hermes_live_natural_router",
  "selected_agent": "Hermes Overseer / Main Agent",
  "selected_model": "qwen3-32b",
  "tool_calls": [
    {
      "tool": "hermes_file_delivery_verify.py",
      "args_preview": "from-message <masked>"
    }
  ],
  "tool_results": [
    {
      "tool": "hermes_file_delivery_verify.py",
      "verification_status": "VERIFIED",
      "telegram_ok": true
    }
  ],
  "evidence_files": [
    "/root/.hermes/artifacts/latest_artifacts.jsonl"
  ],
  "output_quality_status": "verified_direct_response",
  "final_delivery_status": "telegram_text_and_document_sent",
  "errors": [],
  "fallback_used": false,
  "blocked_reason": ""
}
```

Schema notes:

- `router_component` should record the real owner that made the final route decision.
- `tool_calls` and `tool_results` should be separate so failures are visible.
- `evidence_files` should point to transcript, ledger, or artifact files used to justify the answer.
- `output_quality_status` should distinguish:
  - `raw_model_response`
  - `verified_direct_response`
  - `sanitized_model_response`
  - `blocked`
  - `not_verified`
- `final_delivery_status` should distinguish:
  - text only
  - text chunked
  - file delivered
  - file resend delivered
  - blocked
  - failed

## Architecture Verdict

Hermes is not irreparably broken.

Hermes is recoverable, but the live system has architecture drift:

- duplicated message owners
- mixed repo sources of truth
- verified tool routes alongside raw model routes
- early direct responses that bypass a shared final sanitizer
- artifact context resolution based on transcript heuristics

The stabilization problem is architectural, not a single-script bug.
