---
name: Task Reminders
category: automation
purpose: Manage recurring task reminders like upload schedules, meetings, and deadlines.
description: Automate reminders efficiently using cron jobs, delivering notifications directly to Telegram.
---

# Task Reminders Skill

## Purpose

Use this skill to manage recurring task reminders, such as:
- **Upload Schedules:** Notify the user before YouTube uploads.
- **Meetings:** Remind the user before appointments.
- **Tasks:** Alert the user before deadlines.

## Reminder Preference

Reminders should be delivered:
- 6 hours before the event
- 3 hours before the event
- 1 hour before the event

Deliver reminders directly to Telegram.

## Cron Job Setup

Use the `cronjob` tool to create reminders with:
- Clear naming conventions
- Precise timing
- Concise prompts

## User Preferences

Automate reminders efficiently without unnecessary confirmations or questions.

## Deterministic Reminder Creation Rule

For one-shot reminders such as `in 2 minutes`, `in 8 minutes`, `today at 6pm`, and `tomorrow at 7 AM`, Hermes must rely on deterministic cronjob tool parsing in Asia/Shanghai, not model-estimated absolute times.

Success requires:
- the job is written to cron storage
- `next_run_at` exists
- `next_run_at` is in the future
- the tool response includes verification

If verification fails, report `NOT VERIFIED`.

## Phase 7G Recurring Reminder Reliability Rule

- For relative one-shot reminders, use deterministic timedelta parsing in China time.
- For recurring reminders, use deterministic recurrence parsing; do not rely on model-estimated calendar math.
- For schedules like `every Tuesday, Wednesday, Thursday at 15:30`, include today when today's weekday matches and the scheduled time is still in the future.
- Respect `end_date` as an upper bound. Do not describe end-dated recurring jobs as forever schedules.
- Absolute schedules like `once at 2026-05-14 15:30` must parse to that exact Asia/Shanghai wall time, never to a current-time fallback.
- Do not claim a reminder was created unless the job exists, `next_run_at` is correct, and the delivery target is verified.
- Stop after the first verified success. Do not create fallback reminders after a verified cron job was created.
- Do not expose raw tool JSON, call IDs, debug markers, full Telegram chat IDs, tracebacks, tokens, or API keys in normal Telegram replies.
