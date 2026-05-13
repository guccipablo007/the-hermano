# Phase 7I-E: Task-Aware NewCoin Model Router

Goal:
Add a generic model-routing decision layer for Hermes without implementing multi-agent delegation.

Created:
- `/root/.hermes/scripts/hermes_model_router.py`

Updated:
- `/root/.hermes/model_routing/routing_policy.yaml`
- `/root/.hermes/skills/model-router/SKILL.md`

Routing behavior:
- Tool-first routes use verified scripts/tools before model guessing.
- Default/simple route uses NewCoin `qwen3-32b`.
- Reasoning/agentic route uses NewCoin `kimi-k2.6`.
- Coding/debugging route uses NewCoin `deepseek-v3.2`.
- OpenRouter remains fallback only.

Tool-first examples:
- Reminder lookup/listing -> `hermes_reminder_lookup.py`
- Provider/model status -> `hermes_provider_status.py`
- `/btw` recall/status -> `hermes_btw_handler.py` / `hermes_session_recall.py`
- Health/status -> `hermes_ops_healthcheck`

Future planning only:
- `/nc code <task>`
- `/nc reason <task>`
- `/nc cheap <task>`
- `/nc status`

`/nc` was not implemented in this phase.

Verification:
- Explicit classifier tests passed for default, reasoning, coding, app/Firebase/database, reminder tool, and `/btw` provider routes.
- Provider status and provider model tests passed.
- Reminder update, recurring, one-shot create, and one-shot delivery regressions passed.
- Quick/deep healthchecks passed.
- Gateway restarted and startup quick healthcheck passed.

Protected:
- No Gmail/YouTube configuration changed.
- No private_data route activated.
- Reminder logic unchanged.
- No provider keys or auth headers printed.
