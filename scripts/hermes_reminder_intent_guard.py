#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

CHINA_TZ = ZoneInfo("Asia/Shanghai")
JOBS = Path("/root/.hermes/cron/jobs.json")

SECRET_RE = re.compile(r"(bot\d+:[A-Za-z0-9_-]+|Bearer\s+[A-Za-z0-9._:-]+|sk-[A-Za-z0-9_-]+|telegram:[-]?\d{6,}|[-]?\d{8,})", re.I)
REMINDER_RE = re.compile(r"\b(remind\s+me|set\s+a\s+reminder|create\s+a\s+reminder|reminder|reminders|alerts?)\b", re.I)
INQUIRY_RE = re.compile(r"\b(any|do\s+i\s+have|what|show|list)\b.*\b(reminders?|alerts?)\b|\breminders?\s+for\b|\breminder\s+for\b", re.I)
CREATE_RE = re.compile(r"\b(remind\s+me|set\s+a\s+reminder|create\s+a\s+reminder)\b", re.I)
TOMORROW_RE = re.compile(r"\btomorrow\b", re.I)
DATE_RE = re.compile(r"\b(today|tomorrow|tonight|on\s+\w+day|next\s+\w+day|\d{4}-\d{1,2}-\d{1,2}|\d{1,2}/\d{1,2})\b", re.I)
TIME_RE = re.compile(r"\b(at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)\b|\b(at\s+)(\d{1,2}):(\d{2})\b", re.I)
RELATIVE_RE = re.compile(r"\bin\s+\d+\s*(minutes?|mins?|hours?|hrs?|days?)\b", re.I)
TASK_RE = re.compile(r"\b(to|about)\s+(.+)$", re.I)
EVENT_BASED_RE = re.compile(r"\b(before|after)\s+(my\s+)?(.+?)\b", re.I)


def mask(text: Any) -> str:
    return SECRET_RE.sub(lambda m: "telegram:<masked>" if str(m.group(0)).startswith("telegram:") else "<masked>", str(text or ""))


def now_china() -> datetime:
    return datetime.now(CHINA_TZ)


def parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        text = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=CHINA_TZ)
        return dt.astimezone(CHINA_TZ)
    except Exception:
        return None


def load_jobs() -> list[dict[str, Any]]:
    if not JOBS.exists():
        return []
    try:
        data = json.loads(JOBS.read_text(encoding="utf-8"))
        jobs = data.get("jobs") if isinstance(data, dict) else data
        return jobs if isinstance(jobs, list) else []
    except Exception:
        return []


def is_active(job: dict[str, Any]) -> bool:
    if job.get("enabled", True) is False:
        return False
    return str(job.get("state") or "scheduled").lower() in {"scheduled", "pending", "active"}


def delivery_verified(job: dict[str, Any]) -> bool:
    text = json.dumps(job, default=str).lower()
    return "telegram" in text and ("verified" in text or "chat_id" in text or "deliver" in text or "delivery" in text)


def friendly_dt(dt: datetime | None) -> str:
    if not dt:
        return "NOT VERIFIED time"
    return dt.strftime("%A, %B %-d, %Y at %-I:%M %p China time")


def job_label(job: dict[str, Any]) -> str:
    name = str(job.get("name") or job.get("prompt") or "Reminder")
    name = re.sub(r"^Reminder:\s*", "", name, flags=re.I).strip()
    return mask(name[:120])


def jobs_for_window(start: datetime, end: datetime) -> list[dict[str, Any]]:
    matches = []
    for job in load_jobs():
        dt = parse_dt(job.get("next_run_at"))
        if is_active(job) and dt and start <= dt < end:
            matches.append(job)
    return sorted(matches, key=lambda j: parse_dt(j.get("next_run_at")) or datetime.max.replace(tzinfo=CHINA_TZ))


def tomorrow_window() -> tuple[datetime, datetime]:
    n = now_china()
    d = (n + timedelta(days=1)).date()
    start = datetime.combine(d, time.min, tzinfo=CHINA_TZ)
    end = start + timedelta(days=1)
    return start, end


def render_window(matches: list[dict[str, Any]], label: str = "tomorrow") -> str:
    if not matches:
        return f"I checked verified reminder storage and found no reminders for {label}."
    lines = [f"I checked verified reminder storage and found these reminders for {label}:"]
    for job in matches[:12]:
        dt = parse_dt(job.get("next_run_at"))
        delivery = "Telegram DM verified" if delivery_verified(job) else "delivery NOT VERIFIED"
        lines.append(f"- {friendly_dt(dt)} - {job_label(job)}. Delivery: {delivery}.")
    if len(matches) > 12:
        lines.append(f"- {len(matches) - 12} more reminders exist in storage for this window.")
    return "\n".join(lines)


def has_task(text: str) -> bool:
    m = TASK_RE.search(text or "")
    if not m:
        return False
    task = m.group(2).strip().lower()
    # Reject event references as task content for create validation.
    if task in {"my class", "class", "my upload", "upload", "it"}:
        return False
    if re.search(r"\b(before|after)\b", task):
        return False
    return len(task) >= 3


def has_precise_time(text: str) -> bool:
    return bool(TIME_RE.search(text or "") or RELATIVE_RE.search(text or ""))


def has_date_or_relative(text: str) -> bool:
    return bool(DATE_RE.search(text or "") or RELATIVE_RE.search(text or ""))


def event_query(text: str) -> str:
    m = EVENT_BASED_RE.search(text or "")
    if not m:
        return "event"
    q = m.group(3).strip(" ?.!")
    q = re.sub(r"\b(in|at|on|to|before|after)\b.*$", "", q).strip()
    return q or "event"


def search_event_jobs(query: str) -> list[dict[str, Any]]:
    q = query.lower()
    out = []
    for job in load_jobs():
        if not is_active(job) or not parse_dt(job.get("next_run_at")):
            continue
        text = json.dumps(job, default=str).lower()
        if q and q in text:
            out.append(job)
    return sorted(out, key=lambda j: parse_dt(j.get("next_run_at")) or datetime.max.replace(tzinfo=CHINA_TZ))


def classify(text: str) -> dict[str, Any]:
    raw = (text or "").strip()
    low = raw.lower()
    if not REMINDER_RE.search(raw):
        return {"applies": False, "direct_response": False, "category": "not_reminder"}

    start, end = tomorrow_window()
    tomorrow_matches = jobs_for_window(start, end) if TOMORROW_RE.search(raw) else []
    tomorrow_context = render_window(tomorrow_matches, "tomorrow") if TOMORROW_RE.search(raw) else ""

    if EVENT_BASED_RE.search(raw) and CREATE_RE.search(raw):
        q = event_query(raw)
        matches = search_event_jobs(q)
        if len(matches) == 1:
            ctx = render_window(matches, "the matching event")
            msg = ("Your Majesty, I found one possible matching event in verified reminder storage, but I will not create an event-based reminder from memory.\n\n"
                   f"{ctx}\n\nPlease confirm this is the event and the exact reminder offset before I create anything.")
        elif len(matches) > 1:
            ctx = render_window(matches, "matching events")
            msg = ("Your Majesty, I found multiple possible matching events in verified reminder storage.\n\n"
                   f"{ctx}\n\nPlease tell me which event to use. I did not create a reminder.")
        else:
            msg = ("Your Majesty, I could not verify a unique matching event from reminder storage.\n\n"
                   "Please tell me the event date/time or the exact reminder details. I did not create a reminder.")
        return {"applies": True, "direct_response": True, "category": "event_based_needs_verification", "create_allowed": False, "response": msg}

    if INQUIRY_RE.search(raw) and TOMORROW_RE.search(raw):
        msg = f"Your Majesty, {tomorrow_context}\n\nIf you want to create a new reminder, tell me what to remind you about and what time."
        return {"applies": True, "direct_response": True, "category": "tomorrow_inquiry", "create_allowed": False, "response": msg}

    if CREATE_RE.search(raw):
        task = has_task(raw)
        precise_time = has_precise_time(raw)
        date_or_relative = has_date_or_relative(raw)

        if task and precise_time and date_or_relative:
            return {"applies": True, "direct_response": False, "category": "valid_create", "create_allowed": True, "verification_required": True}

        if TOMORROW_RE.search(raw) and not task and not precise_time:
            msg = (f"Your Majesty, {tomorrow_context}\n\n"
                   "To create a new reminder for tomorrow, please tell me both what to remind you about and what time. I did not create anything.")
            return {"applies": True, "direct_response": True, "category": "ambiguous_create_missing_task_time", "create_allowed": False, "response": msg}

        if date_or_relative and task and not precise_time:
            msg = "Your Majesty, what time should I remind you? I did not create anything."
            if TOMORROW_RE.search(raw):
                msg = f"Your Majesty, {tomorrow_context}\n\nWhat time tomorrow should I remind you? I did not create anything."
            return {"applies": True, "direct_response": True, "category": "missing_time", "create_allowed": False, "response": msg}

        if date_or_relative and precise_time and not task:
            msg = "Your Majesty, what should I remind you about? I did not create anything."
            if TOMORROW_RE.search(raw):
                msg = f"Your Majesty, {tomorrow_context}\n\nWhat should I remind you about? I did not create anything."
            return {"applies": True, "direct_response": True, "category": "missing_task", "create_allowed": False, "response": msg}

        msg = "Your Majesty, I need the reminder task and the date/time before creating anything."
        return {"applies": True, "direct_response": True, "category": "ambiguous_create", "create_allowed": False, "response": msg}

    if re.fullmatch(r"\s*reminders?\??\s*", raw, re.I) or re.fullmatch(r"\s*reminder\??\s*", raw, re.I):
        return {"applies": True, "direct_response": True, "category": "ambiguous_reminder", "create_allowed": False, "response": "Your Majesty, do you want me to show your existing reminders or create a new one? I did not create anything."}

    return {"applies": False, "direct_response": False, "category": "not_guarded"}


def main() -> int:
    p = argparse.ArgumentParser(description="Query-first guard for ambiguous Hermes reminder requests.")
    p.add_argument("message")
    p.add_argument("--format", choices=["json", "friendly"], default="json")
    args = p.parse_args()
    result = classify(args.message)
    if args.format == "friendly":
        if result.get("direct_response"):
            print(mask(result.get("response", "")))
        else:
            print("REMINDER_INTENT_VALID_CREATE" if result.get("create_allowed") else "REMINDER_INTENT_NOT_GUARDED")
            print("category=" + str(result.get("category")))
            print("verification_required=" + str(bool(result.get("verification_required"))))
    else:
        print(mask(json.dumps(result, ensure_ascii=False, indent=2)))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
