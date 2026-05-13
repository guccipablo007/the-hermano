# Phase 7J-B: Safe Live Agent Preview

Goal:
Wire read-only live Telegram agent-preview behavior for the Phase 7J four-agent framework without enabling live delegation execution.

Changed:
- Updated `/root/.hermes/scripts/hermes_live_natural_router.py`.
- Added natural-language agent-preview intent handling for:
  - which/what agent questions
  - who handles questions
  - what agents are available
  - delegated task status questions
  - attempts to run delegated tasks from live Telegram

Behavior:
- Agent-preview questions call `/root/.hermes/scripts/hermes_agent_delegate.py classify`.
- Recent delegated task questions call `/root/.hermes/scripts/hermes_agent_delegate.py status`.
- Requests to execute delegated tasks from live Telegram are blocked with a safe dry-run offer.
- The live response lists exactly four agents and no additional specialist agents.
- Reminder, provider/model, `/btw`, and natural-language model routing remain unchanged.

Safety:
- Live delegation execution remains disabled.
- No more than four agents are listed.
- No YouTube agent was added.
- No Gmail/YouTube/private_data route was configured or activated.
- No provider keys, auth headers, bot tokens, OAuth tokens, passwords, or full Telegram chat IDs are printed.

Verification:
- Python syntax checks passed.
- Firebase/app preview returns Apps, Coding & Complex Builds Agent.
- Gateway health preview returns Ops & Verification Agent.
- Reminder/lesson-plan preview returns Personal/Admin & Tutor Agent.
- Agent list returns exactly the four configured agents.
- Delegated task status returns storage-backed ledger records.
- Live execution request is blocked.
- Model router, provider status, `/btw`, reminder update, recurring reminders, one-shot create, one-shot delivery, quick healthcheck, and deep healthcheck regressions passed.

Gateway:
- Gateway was not restarted because the live direct-preview path invokes the router script as a subprocess.
