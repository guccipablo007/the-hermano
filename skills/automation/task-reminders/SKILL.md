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
