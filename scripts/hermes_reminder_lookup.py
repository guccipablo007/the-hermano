#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

JOBS_FILE = Path("/root/.hermes/cron/jobs.json")
CHINA_TZ = ZoneInfo("Asia/Shanghai")
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SECRET_PATTERNS = [
    (re.compile(r"bot\d+:[A-Za-z0-9_-]+"), "bot<REDACTED>"),
    (re.compile(r"Bearer\s+[A-Za-z0-9._-]+", re.I), "Bearer <REDACTED>"),
    (re.compile(r"(telegram:)-?\d+"), r"\1<chat_id_masked>"),
    (re.compile(r'("chat_id"\s*:\s*)-?\d+'), r'\1"<chat_id_masked>"'),
]
STOPWORDS = {"when", "is", "my", "next", "reminder", "reminders", "the", "a", "an", "show", "list", "scheduled", "all", "me", "what", "do", "i", "have", "are", "active", "please", "tell"}


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
        days = ", ".join(WEEKDAY_NAMES[int(d)] for d in schedule.get("weekdays", []) if 0 <= int(d) <= 6)
        return f"every {days} at {schedule.get('time')}"
    if schedule.get("kind") == "once":
        return "once at " + str(schedule.get("run_at"))
    return json.dumps(schedule, ensure_ascii=False)


def delivery_text(job: dict) -> str:
    deliver = str(job.get("deliver") or "local")
    origin = job.get("origin") or {}
    target = job.get("delivery_target") or {}
    if isinstance(target, dict) and str(target.get("type", "")).lower() == "telegram":
        return "telegram:<chat_id_masked>" if target.get("chat_id") else "telegram:NOT_VERIFIED"
    if deliver == "origin" and origin.get("platform"):
        present = bool(origin.get("chat_id"))
        return f"{origin.get('platform')}:<chat_id_masked>" if present else f"{origin.get('platform')}:NOT_VERIFIED"
    if deliver.startswith("telegram:"):
        return "telegram:<chat_id_masked>"
    return mask(deliver)


def delivery_verified(job: dict) -> bool:
    value = delivery_text(job)
    return value.startswith("telegram:") and "NOT_VERIFIED" not in value


def parse_dt(value: object):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value)).astimezone(CHINA_TZ)
    except Exception:
        return None


def active(job: dict) -> bool:
    state = str(job.get("state", "scheduled")).lower()
    return bool(job.get("enabled", True)) and state not in {"paused", "completed", "error", "disabled"}


def searchable_text(job: dict) -> str:
    parts = [job.get("id"), job.get("name"), job.get("prompt"), job.get("schedule_display"), json.dumps(job.get("schedule") or {}, ensure_ascii=False), str(job.get("last_status") or "")]
    return " ".join(str(p or "") for p in parts).lower()


def query_tokens(query: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9']+", (query or "").lower())
    return [t for t in tokens if t not in STOPWORDS]


def token_match(job: dict, query: str) -> bool:
    tokens = query_tokens(query)
    if not tokens:
        return True
    hay = searchable_text(job)
    if len(tokens) >= 2:
        return all(t in hay for t in tokens)
    return any(t in hay for t in tokens)


def score_job(job: dict, query: str) -> int:
    hay = searchable_text(job)
    tokens = query_tokens(query)
    score = sum(10 for token in tokens if token in hay)
    q = (query or "").lower().strip()
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
        matches = [j for _, j in scored if q and q in searchable_text(j)]
    return sort_jobs(matches)


def job_summary(job: dict) -> list[str]:
    return [f"job_id: {job.get('id')}", f"name: {mask(job.get('name'))}", f"schedule: {mask(schedule_text(job))}", f"next_run_at: {mask(job.get('next_run_at'))}", f"enabled/state: {bool(job.get('enabled', True))}/{job.get('state', 'scheduled')}", f"last_status: {mask(job.get('last_status'))}", f"delivery: {delivery_text(job)}"]


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
        extra = [j for j in active_matches if j.get("id") != earliest.get("id")]
        if extra:
            lines.append("MATCH_COUNT=" + str(len(active_matches)))
            for j in sort_jobs(extra)[:8]:
                lines.append("MATCH")
                lines.extend(job_summary(j))
        return "\n".join(lines)
    lines.append("MATCH_COUNT=" + str(len(matches)))
    for j in matches[:25]:
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
    h = hour % 12 or 12
    return f"{h}:{minute:02d} {suffix}"


def join_words(values: list[str]) -> str:
    if len(values) <= 1:
        return values[0] if values else ""
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return ", ".join(values[:-1]) + f", and {values[-1]}"


def friendly_schedule(job: dict) -> str:
    schedule = job.get("schedule") or {}
    if schedule.get("kind") == "weekly":
        days = [WEEKDAY_NAMES[int(d)] for d in schedule.get("weekdays", []) if 0 <= int(d) <= 6]
        hour, minute = [int(x) for x in str(schedule.get("time", "00:00")).split(":", 1)]
        return f"Every {join_words(days)} at {friendly_time(hour, minute)}."
    text = schedule_text(job)
    match = re.match(r"every\s+(.+?)\s+at\s+(\d{1,2}):(\d{2})", text, flags=re.I)
    if match:
        days = [d.strip().capitalize() for d in re.split(r",\s*", match.group(1)) if d.strip()]
        return f"Every {join_words(days)} at {friendly_time(int(match.group(2)), int(match.group(3)))}."
    return mask(text)


def clean_job_name(name: str) -> str:
    value = re.sub(r"^Reminder:\s*", "", str(name or ""), flags=re.I).strip()
    return re.sub(r"\s+", " ", value)


def _friendly_label_case(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return "reminder"
    return text[:1].upper() + text[1:].lower()


def derive_label(query: str, job: dict | None = None) -> str:
    tokens = query_tokens(query)
    if job and len(tokens) <= 1:
        name = clean_job_name(str(job.get("name") or ""))
        name = re.sub(r"'s\b", "", name, flags=re.I)
        name = re.sub(r"\s+starts\s+in\s+.+$", "", name, flags=re.I)
        name = re.sub(r"\s+-\s+\d+\s+hours?\s+before$", "", name, flags=re.I)
        name = re.sub(r"\s+-\s+\d+\s+hours?\s+reminder$", "", name, flags=re.I)
        if tokens and re.search(r"\bclass\b", name, flags=re.I):
            return _friendly_label_case(tokens[0] + " class reminder")
        if name:
            label = name if name.lower().endswith("reminder") else name + " reminder"
            return _friendly_label_case(label)
    if tokens:
        return _friendly_label_case(" ".join(tokens) + " reminder")
    return "reminder"


def offset_group_info(job: dict):
    text = clean_job_name(str(job.get("name") or ""))
    match = re.search(r"^(?P<base>.+?)\s+(?:-|\?|:)?\s*(?P<offset>\d+)\s+hours?\s+before\s*$", text, flags=re.I)
    if not match:
        prompt = str(job.get("prompt") or "")
        pm = re.search(r"your\s+(?P<offset>\d+)\s*-?hour\s+reminder", prompt, flags=re.I)
        if not pm:
            return None
        base = re.sub(r"\s*-?\s*\d+\s+hours?\s+before\s*$", "", text, flags=re.I).strip() or "Reminder"
        return base, int(pm.group("offset"))
    return match.group("base").strip(), int(match.group("offset"))


def infer_event_time(job: dict) -> str | None:
    prompt = str(job.get("prompt") or "")
    match = re.search(r"scheduled\s+for\s+(\d{1,2})(?::(\d{2}))?\s*(AM|PM)", prompt, flags=re.I)
    if match:
        return f"{int(match.group(1))}:{match.group(2) or '00'} {match.group(3).upper()}"
    return None


def delivery_line(jobs: list[dict]) -> str:
    return "Delivery: Telegram DM verified." if jobs and all(delivery_verified(j) for j in jobs) else "Delivery: NOT VERIFIED."


def friendly_job_line(job: dict, query: str = "") -> str:
    label = derive_label(query, job)
    info = offset_group_info(job)
    if info:
        _, offset = info
        label = f"{offset}-hour reminder"
    return f"- {friendly_dt(parse_dt(job.get('next_run_at')))} - {label}. {friendly_schedule(job)}"


def group_offset_jobs(jobs: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for job in jobs:
        info = offset_group_info(job)
        if info:
            base, _ = info
            groups[base].append(job)
    return groups


def render_offset_group(base: str, jobs: list[dict]) -> list[str]:
    sorted_group = sort_jobs(jobs)
    heading = base if base.lower().endswith("reminders") else base + "s"
    lines = [heading]
    for job in sorted_group:
        info = offset_group_info(job)
        offset = info[1] if info else None
        suffix = f"{offset}-hour reminder" if offset else "reminder"
        lines.append(f"- {friendly_dt(parse_dt(job.get('next_run_at')))} - {suffix}.")
    event_time = next((infer_event_time(j) for j in sorted_group if infer_event_time(j)), None)
    if event_time:
        schedule = sorted_group[0].get("schedule") or {}
        if schedule.get("kind") == "weekly" and schedule.get("weekdays"):
            day = WEEKDAY_NAMES[int(schedule.get("weekdays")[0])]
            lines.append(f"Upload time: {day} at {event_time} China time.")
        else:
            lines.append(f"Upload time: {event_time} China time.")
    lines.append(delivery_line(sorted_group))
    return lines


def render_friendly_list(jobs: list[dict]) -> str:
    active_jobs = sort_jobs([j for j in jobs if active(j) and parse_dt(j.get("next_run_at")) and delivery_verified(j)])
    if not active_jobs:
        return "Your Majesty, I could not verify any active reminders from storage.\n\nNOT VERIFIED"
    lines = ["Your Majesty, these are your verified active reminders from storage:"]
    grouped_ids = set()
    groups = group_offset_jobs(active_jobs)
    for base, grouped in sorted(groups.items(), key=lambda item: parse_dt(sort_jobs(item[1])[0].get("next_run_at")) or datetime.max.replace(tzinfo=CHINA_TZ)):
        lines.append("")
        lines.extend(render_offset_group(base, grouped))
        grouped_ids.update(str(j.get("id")) for j in grouped)
    remaining = [j for j in active_jobs if str(j.get("id")) not in grouped_ids]
    if remaining:
        lines.append("")
        lines.append("Other Reminders")
        for job in remaining:
            lines.append(friendly_job_line(job))
            lines.append(delivery_line([job]))
    return "\n".join(lines)


def render_friendly(matches: list[dict], *, mode: str, query: str = "") -> str:
    if mode == "list":
        return render_friendly_list(matches)
    if not matches:
        return "Your Majesty, I could not verify a matching reminder from storage.\n\nNOT VERIFIED"
    active_matches = [j for j in matches if active(j) and parse_dt(j.get("next_run_at"))]
    if mode == "next" and not active_matches:
        return "Your Majesty, I could not verify a matching active reminder with a next run time from storage.\n\nNOT VERIFIED"
    if mode == "next":
        earliest = sort_jobs(active_matches)[0]
        info = offset_group_info(earliest)
        label = derive_label(query, earliest)
        if info:
            _, offset = info
            label = f"{label} ({offset}-hour reminder)"
        lines = [f"Your Majesty, your next {label} is {friendly_dt(parse_dt(earliest.get('next_run_at')))}.", "", f"Schedule: {friendly_schedule(earliest)}"]
        event_time = infer_event_time(earliest)
        if event_time:
            lines.append(f"Upload time: {event_time} China time.")
        lines.append("Delivery: Telegram DM verified." if delivery_verified(earliest) else "Delivery: NOT VERIFIED.")
        extras = [j for j in active_matches if j.get("id") != earliest.get("id")]
        if extras:
            lines.append("")
            lines.append("I found multiple matching reminders. Earliest is shown above; other matches:")
            for job in sort_jobs(extras)[:8]:
                lines.append(friendly_job_line(job, query))
        return "\n".join(lines)
    return render_friendly_list(matches)


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
                return "\n".join([f"Your Majesty, I verified this reminder from storage: {mask(job.get('name'))}.", f"Schedule: {friendly_schedule(job)}", f"Next reminder: {friendly_dt(parse_dt(job.get('next_run_at')))}.", "Delivery: Telegram DM verified." if delivery_verified(job) else "Delivery: NOT VERIFIED."])
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
        if args.mode == "list":
            out = list_mode(fmt)
        elif args.mode == "search":
            out = search_mode(args.query, fmt)
        elif args.mode == "next":
            out = next_mode(args.query, fmt)
        elif args.mode == "status":
            out = status_mode(args.job_id, fmt)
        else:
            out = "NOT VERIFIED\nREASON=UNKNOWN_MODE"
    except Exception as exc:
        out = f"NOT VERIFIED\nREASON=LOOKUP_EXCEPTION:{type(exc).__name__}:{exc}"
    print(mask(out))
    return 2 if "NOT VERIFIED" in out else 0


if __name__ == "__main__":
    raise SystemExit(main())
