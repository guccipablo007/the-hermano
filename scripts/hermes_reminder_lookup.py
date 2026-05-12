#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

JOBS_FILE = Path("/root/.hermes/cron/jobs.json")
CHINA_TZ = ZoneInfo("Asia/Shanghai")
SECRET_PATTERNS = [
    (re.compile(r"bot\d+:[A-Za-z0-9_-]+"), "bot<REDACTED>"),
    (re.compile(r"Bearer\s+[A-Za-z0-9._-]+", re.I), "Bearer <REDACTED>"),
    (re.compile(r"(telegram:)-?\d+"), r"\1<chat_id_masked>"),
]
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def mask(text: object) -> str:
    value = str(text or "")
    for pat, repl in SECRET_PATTERNS:
        value = pat.sub(repl, value)
    return value


def load_jobs() -> list[dict]:
    if not JOBS_FILE.exists():
        raise FileNotFoundError(str(JOBS_FILE))
    data = json.loads(JOBS_FILE.read_text())
    jobs = data.get("jobs", data) if isinstance(data, dict) else data
    if not isinstance(jobs, list):
        raise ValueError("cron jobs storage is not a list")
    return jobs


def schedule_text(job: dict) -> str:
    schedule = job.get("schedule") or {}
    if job.get("schedule_display"):
        return str(job.get("schedule_display"))
    if schedule.get("display"):
        return str(schedule.get("display"))
    if schedule.get("kind") == "cron":
        return str(schedule.get("expr"))
    if schedule.get("kind") == "weekly":
        days = ",".join(str(d) for d in schedule.get("weekdays", []))
        return f"weekly({days}) at {schedule.get('time')}"
    if schedule.get("kind") == "once":
        return "once at " + str(schedule.get("run_at"))
    return json.dumps(schedule, ensure_ascii=False)


def delivery_text(job: dict) -> str:
    deliver = str(job.get("deliver") or "local")
    origin = job.get("origin") or {}
    if deliver == "origin" and origin.get("platform"):
        present = bool(origin.get("chat_id"))
        return f"{origin.get('platform')}:<chat_id_masked>" if present else f"{origin.get('platform')}:NOT_VERIFIED"
    if deliver.startswith("telegram:"):
        return "telegram:<chat_id_masked>"
    return mask(deliver)


def delivery_verified(job: dict) -> bool:
    return delivery_text(job).startswith("telegram:") and "NOT_VERIFIED" not in delivery_text(job)


def parse_dt(value: object):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value)).astimezone(CHINA_TZ)
    except Exception:
        return None


def active(job: dict) -> bool:
    return bool(job.get("enabled", True)) and str(job.get("state", "scheduled")) not in {"paused", "completed", "error"}


def searchable_text(job: dict) -> str:
    parts = [
        job.get("id"), job.get("name"), job.get("prompt"), job.get("schedule_display"),
        json.dumps(job.get("schedule") or {}, ensure_ascii=False), str(job.get("last_status") or ""),
    ]
    return " ".join(str(p or "") for p in parts).lower()


def query_tokens(query: str) -> list[str]:
    q = (query or "").lower()
    aliases = {
        "mickey": ["mickey", "class"],
        "sunday upload": ["sunday", "upload"],
        "upload reminder": ["upload", "reminder"],
    }
    tokens = re.findall(r"[a-z0-9']+", q)
    expanded = list(tokens)
    for phrase, extra in aliases.items():
        if phrase in q:
            expanded.extend(extra)
    stop = {"when", "is", "my", "next", "reminder", "the", "a", "an", "class"}
    result = [t for t in expanded if t not in stop]
    return result or [t for t in tokens if t]


def token_match(job: dict, query: str) -> bool:
    tokens = query_tokens(query)
    if not tokens:
        return True
    hay = searchable_text(job)
    if len(tokens) >= 2:
        return all(token in hay for token in tokens)
    return any(token in hay for token in tokens)


def score_job(job: dict, query: str) -> int:
    hay = searchable_text(job)
    tokens = query_tokens(query)
    score = 0
    for token in tokens:
        if token in hay:
            score += 10
    q = (query or "").lower()
    name = str(job.get("name") or "").lower()
    prompt = str(job.get("prompt") or "").lower()
    if q and q in name:
        score += 50
    if q and q in prompt:
        score += 30
    if active(job):
        score += 5
    if parse_dt(job.get("next_run_at")):
        score += 3
    return score


def sort_jobs(jobs: list[dict]) -> list[dict]:
    def key(job):
        dt = parse_dt(job.get("next_run_at"))
        return (0 if active(job) else 1, dt or datetime.max.replace(tzinfo=CHINA_TZ), str(job.get("name") or ""))
    return sorted(jobs, key=key)


def find_jobs(query: str) -> list[dict]:
    jobs = load_jobs()
    scored = [(score_job(j, query), j) for j in jobs if token_match(j, query)]
    matches = [j for score, j in scored if score >= 10]
    if not matches and query:
        q = query.lower().strip()
        matches = [j for score, j in scored if q and q in searchable_text(j)]
    return sort_jobs(matches)


def job_summary(job: dict) -> list[str]:
    return [
        f"job_id: {job.get('id')}",
        f"name: {mask(job.get('name'))}",
        f"schedule: {mask(schedule_text(job))}",
        f"next_run_at: {mask(job.get('next_run_at'))}",
        f"enabled/state: {bool(job.get('enabled', True))}/{job.get('state', 'scheduled')}",
        f"last_status: {mask(job.get('last_status'))}",
        f"delivery: {delivery_text(job)}",
    ]


def render_raw(matches: list[dict], *, mode: str, query: str = "") -> str:
    if not matches:
        return "NOT VERIFIED\nREASON=NO_MATCHING_ACTIVE_REMINDER_EVIDENCE"
    lines = ["VERIFIED"]
    if mode == "next":
        active_matches = [j for j in matches if active(j) and parse_dt(j.get("next_run_at"))]
        if not active_matches:
            return "NOT VERIFIED\nREASON=NO_ACTIVE_MATCH_WITH_NEXT_RUN"
        earliest = sort_jobs(active_matches)[0]
        lines.append("EARLIEST_NEXT_REMINDER")
        lines.extend(job_summary(earliest))
        extra = [j for j in matches if j.get("id") != earliest.get("id")]
        if extra:
            lines.append("MATCH_COUNT=" + str(len(matches)))
            for j in sort_jobs(extra)[:4]:
                lines.append("MATCH")
                lines.extend(job_summary(j))
        return "\n".join(lines)
    lines.append("MATCH_COUNT=" + str(len(matches)))
    for j in matches[:10]:
        lines.append("MATCH")
        lines.extend(job_summary(j))
    return "\n".join(lines)


def friendly_dt(dt: datetime | None) -> str:
    if not dt:
        return "NOT VERIFIED"
    hour = dt.strftime("%I").lstrip("0") or "0"
    day = dt.strftime("%d").lstrip("0") or "0"
    return f"{dt.strftime('%A')}, {dt.strftime('%B')} {day}, {dt.strftime('%Y')} at {hour}:{dt.strftime('%M')} {dt.strftime('%p')} China time"


def friendly_time(hour: int, minute: int) -> str:
    suffix = "AM" if hour < 12 else "PM"
    h = hour % 12
    if h == 0:
        h = 12
    return f"{h}:{minute:02d} {suffix}"


def join_days(days: list[str]) -> str:
    if len(days) <= 1:
        return days[0] if days else ""
    if len(days) == 2:
        return f"{days[0]} and {days[1]}"
    return ", ".join(days[:-1]) + f", and {days[-1]}"


def friendly_schedule(job: dict) -> str:
    schedule = job.get("schedule") or {}
    if schedule.get("kind") == "weekly":
        days = [WEEKDAY_NAMES[int(d)] for d in schedule.get("weekdays", []) if 0 <= int(d) <= 6]
        hour, minute = [int(x) for x in str(schedule.get("time", "00:00")).split(":", 1)]
        return f"Every {join_days(days)} at {friendly_time(hour, minute)}."
    text = schedule_text(job)
    match = re.match(r"every\s+(.+?)\s+at\s+(\d{1,2}):(\d{2})", text, flags=re.I)
    if match:
        days = [d.strip().capitalize() for d in re.split(r",\s*", match.group(1)) if d.strip()]
        return f"Every {join_days(days)} at {friendly_time(int(match.group(2)), int(match.group(3)))}."
    return mask(text)


def friendly_label(query: str, job: dict | None = None) -> str:
    q = (query or "").strip().lower()
    if "mickey" in q or (job and "mickey" in str(job.get("name", "")).lower()):
        return "Mickey class reminder"
    if "sunday" in q and "upload" in q:
        return "Sunday upload reminder"
    if "upload" in q:
        return "upload reminder"
    cleaned = re.sub(r"\b(when|is|my|next|the|a|an|reminder)\b", "", q).strip()
    return (cleaned + " reminder").strip().capitalize() if cleaned else "reminder"


def friendly_job_line(job: dict, query: str) -> str:
    label = friendly_label(query, job)
    return f"- {label}: {friendly_dt(parse_dt(job.get('next_run_at')))}; {friendly_schedule(job)}"


def render_friendly(matches: list[dict], *, mode: str, query: str = "") -> str:
    if not matches:
        return "Your Majesty, I could not verify a matching reminder from storage.\n\nNOT VERIFIED"
    active_matches = [j for j in matches if active(j) and parse_dt(j.get("next_run_at"))]
    if mode == "next" and not active_matches:
        return "Your Majesty, I could not verify a matching active reminder with a next run time from storage.\n\nNOT VERIFIED"
    if mode == "next":
        earliest = sort_jobs(active_matches)[0]
        label = friendly_label(query, earliest)
        lines = [
            f"Your Majesty, your next {label} is {friendly_dt(parse_dt(earliest.get('next_run_at')))}.",
            "",
            f"Schedule: {friendly_schedule(earliest)}",
            "Delivery: Telegram DM verified." if delivery_verified(earliest) else "Delivery: NOT VERIFIED.",
        ]
        extras = [j for j in active_matches if j.get("id") != earliest.get("id")]
        if extras:
            lines.append("")
            lines.append("I found multiple matching reminders. Earliest is shown above; other matches:")
            for job in sort_jobs(extras)[:4]:
                lines.append(friendly_job_line(job, query))
        return "\n".join(lines)
    lines = ["Your Majesty, I found these matching reminders from storage:"]
    for job in sort_jobs(matches)[:10]:
        lines.append(friendly_job_line(job, query))
    return "\n".join(lines)


def list_mode(fmt: str) -> str:
    jobs = sort_jobs([j for j in load_jobs() if active(j)])
    if fmt == "friendly":
        return render_friendly(jobs, mode="list")
    if not jobs:
        return "NOT VERIFIED\nREASON=NO_ACTIVE_REMINDERS_FOUND"
    return render_raw(jobs, mode="list")


def search_mode(query: str, fmt: str) -> str:
    matches = find_jobs(query)
    return render_friendly(matches, mode="search", query=query) if fmt == "friendly" else render_raw(matches, mode="search", query=query)


def next_mode(query: str, fmt: str) -> str:
    matches = find_jobs(query)
    return render_friendly(matches, mode="next", query=query) if fmt == "friendly" else render_raw(matches, mode="next", query=query)


def status_mode(job_id: str, fmt: str) -> str:
    for job in load_jobs():
        if str(job.get("id")) == str(job_id):
            if fmt == "friendly":
                return "\n".join([
                    f"Your Majesty, I verified this reminder from storage: {mask(job.get('name'))}.",
                    f"Schedule: {friendly_schedule(job)}",
                    f"Next reminder: {friendly_dt(parse_dt(job.get('next_run_at')))}.",
                    "Delivery: Telegram DM verified." if delivery_verified(job) else "Delivery: NOT VERIFIED.",
                ])
            return "VERIFIED\n" + "\n".join(job_summary(job))
    return "Your Majesty, I could not verify that reminder from storage.\n\nNOT VERIFIED" if fmt == "friendly" else "NOT VERIFIED\nREASON=JOB_NOT_FOUND"


def add_format_arg(parser):
    parser.add_argument("--format", choices=["raw", "friendly"], default="raw")


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Hermes reminder lookup from cron storage.")
    sub = parser.add_subparsers(dest="mode", required=True)
    p_list = sub.add_parser("list"); add_format_arg(p_list)
    p_search = sub.add_parser("search"); p_search.add_argument("query"); add_format_arg(p_search)
    p_next = sub.add_parser("next"); p_next.add_argument("query"); add_format_arg(p_next)
    p_status = sub.add_parser("status"); p_status.add_argument("job_id"); add_format_arg(p_status)
    args = parser.parse_args()
    fmt = getattr(args, "format", "raw")
    try:
        if args.mode == "list": out = list_mode(fmt)
        elif args.mode == "search": out = search_mode(args.query, fmt)
        elif args.mode == "next": out = next_mode(args.query, fmt)
        elif args.mode == "status": out = status_mode(args.job_id, fmt)
        else: out = "NOT VERIFIED\nREASON=UNKNOWN_MODE"
    except Exception as exc:
        out = f"NOT VERIFIED\nREASON=LOOKUP_EXCEPTION:{type(exc).__name__}:{exc}"
    print(mask(out))
    return 0 if (out.startswith("VERIFIED") or not "NOT VERIFIED" in out) else 2

if __name__ == "__main__":
    raise SystemExit(main())
