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

## Phase 7G-C Reminder Lookup Accuracy Rule

- For reminder lookup questions, always query cron storage through `/root/.hermes/scripts/hermes_reminder_lookup.py`.
- Never answer next-reminder or schedule lookup questions from memory, session summaries, or inferred user intent.
- If cron storage evidence is missing or inaccessible, say `NOT VERIFIED`.
- Reminder lookup is read-only: do not create, edit, pause, resume, delete, or run jobs during lookup.
- For multiple matches, list matching jobs and identify the earliest `next_run_at` from active enabled jobs.
- Mask Telegram chat IDs and never expose raw JSON/tool payloads in normal Telegram replies.

## General Natural-Language Reminder Rules - Phase 7G-E

Reminder behavior must be storage-backed and deterministic, not based on memory guesses.

Rules:
- Relative one-shot reminders use deterministic timedelta parsing.
- Absolute one-shot reminders such as `once at YYYY-MM-DD HH:MM` use deterministic date/time parsing in Asia/Shanghai.
- Weekly recurring reminders use deterministic weekday/time parsing.
- Same-day future occurrences are included.
- Same-day past occurrences move to the next valid weekday.
- End dates are upper bounds and must not be exceeded.
- Multi-reminder offset requests create one verified job per offset unless a multi-time schedule format is explicitly verified.
- List and lookup requests always read cron storage.
- Friendly Telegram output is the default for lookup/list responses.
- Raw technical output is only for explicit debug/technical requests.
- If parsing, storage lookup, next_run_at verification, or delivery target verification fails, answer NOT VERIFIED.
- Do not claim created, scheduled, updated, or delivered without verified storage and delivery evidence.
- Do not expose raw tool JSON, full chat IDs, tokens, or API keys.
