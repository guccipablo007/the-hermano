# Phase 7J-C: Telegram Dry-Run Delegation Planning

Goal:
Allow live Telegram to create dry-run delegation plans only. Live delegated execution remains disabled.

Changes:
- Updated `/root/.hermes/scripts/hermes_agent_delegate.py` so `delegate --dry-run` creates:
  - a task ledger entry marked `planned`
  - a dry-run report under `/root/.hermes/agent_tasks/reports/`
  - required user inputs
  - proposed actions
  - prohibited actions
  - verification status `NOT_EXECUTED_DRY_RUN`
- Updated `/root/.hermes/scripts/hermes_agent_report_verify.py` to recognize dry-run plans as `NOT_EXECUTED_DRY_RUN`, not fake `VERIFIED` execution.
- Updated `/root/.hermes/scripts/hermes_live_natural_router.py` so natural-language dry-run planning requests call `hermes_agent_delegate.py delegate ... --dry-run`.
- Live execution requests remain blocked and offer dry-run planning instead.

Safety:
- Dry-runs do not execute commands.
- Dry-runs do not edit files except the intended task ledger/report files.
- Dry-runs do not restart services.
- Dry-runs do not create, delete, or modify reminders.
- Dry-runs do not call destructive tools.
- No more than four agents are defined.
- No YouTube agent was added.
- Gmail/YouTube/private_data remain untouched.

Verification:
- Firebase dry-run delegation assigned Apps, Coding & Complex Builds Agent using NewCoin `deepseek-v3.2`.
- Gateway health dry-run delegation assigned Ops & Verification Agent using tool-first verification.
- Reminder dry-run delegation assigned Personal/Admin & Tutor Agent and preserved query-first reminder behavior.
- Lesson-plan dry-run delegation assigned Personal/Admin & Tutor Agent.
- Task status is storage-backed from `/root/.hermes/agent_tasks/tasks.jsonl`.
- Dry-run report verification returns `NOT_EXECUTED_DRY_RUN`.
- Model router, provider status, `/btw`, reminder intent guard, reminder update, recurring reminder, one-shot create, one-shot delivery, quick healthcheck, and deep healthcheck regressions passed.
- Gateway restarted and startup quick healthcheck passed.
