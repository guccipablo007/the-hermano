# Phase 7J-B2: Query-First Reminder Handling

Goal:
Prevent ambiguous natural-language reminder messages from falling through to generic model guessing or unverified reminder creation.

Root cause:
Ambiguous reminder messages such as "Reminder for tomorrow?" and "Remind me tomorrow" were classified as default/simple model traffic. That allowed the generic model path to infer intent and potentially claim scheduling behavior without first checking verified reminder storage.

Changes:
- Added `/root/.hermes/scripts/hermes_reminder_intent_guard.py`.
- Added `/root/.hermes/scripts/hermes_reminder_intent_validation_test.py`.
- Updated `/root/.hermes/scripts/hermes_live_natural_router.py` to run the reminder guard before generic model fallback.
- Updated `/root/.hermes/scripts/hermes_model_router.py` so ambiguous tomorrow reminder phrasing is tool-first via `hermes_reminder_intent_guard`.
- Updated `/root/.hermes/skills/automation/task-reminders/SKILL.md` with query-first reminder rules.
- Updated `/root/.hermes/agents/personal_admin_tutor_agent.yaml` with query-first reminder rules.

Behavior:
- Reminder inquiries for tomorrow query verified storage first.
- Ambiguous create requests query storage first, then ask for missing task/time.
- Missing-time and missing-task requests do not create anything.
- Fully specified create requests are allowed to continue to the existing creation path, but success still requires post-create storage verification.
- Event-based reminders require a unique verified event before creation.
- No upload/class/event schedule is guessed from memory.

Suspicious job audit:
- Recent non-test reminder jobs with class/upload/reminder terms were listed as `SUSPECT_REQUIRES_USER_CONFIRMATION`.
- No reminders were deleted or modified in this phase.
- No specific bad ambiguous-created job was verified from storage/logs during this phase.

Verification:
- Ambiguous tomorrow inquiry test passed.
- Reminder inquiry test passed.
- Ambiguous create test passed.
- Missing-time test passed.
- Missing-task test passed.
- Valid tomorrow create intent test passed.
- Relative valid create intent test passed.
- Event-based reminder verification test passed.
- No-create-call invariant passed.
- Reminder update, recurring reminder, one-shot create, one-shot delivery, agent reminder classification, model router, provider status, `/btw`, quick healthcheck, and deep healthcheck regressions passed.
- Gateway restarted and startup quick healthcheck passed.

Protected:
- No Gmail/YouTube configuration changed.
- No private_data route activated.
- Provider/model routing preserved.
- `/btw`, live natural-language router, and 4-agent preview behavior preserved.
- No full Telegram chat IDs or provider keys printed.
