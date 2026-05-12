#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
import sys
from datetime import datetime, time as dt_time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Shanghai")
AGENT_ROOT = Path("/usr/local/lib/hermes-agent")
JOBS_PATH = AGENT_ROOT / "cron" / "jobs.py"
TOOLS_PATH = AGENT_ROOT / "tools" / "cronjob_tools.py"
LOOKUP_PATH = Path("/root/.hermes/scripts/hermes_reminder_lookup.py")
GATEWAY_PATH = AGENT_ROOT / "gateway" / "run.py"


def load_module(name: str, path: Path):
    sys.path.insert(0, str(AGENT_ROOT))
    sys.path.insert(0, str(AGENT_ROOT / "tools"))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def fail(case: str, detail: str) -> None:
    print("NOT VERIFIED")
    print(f"FAILED_CASE={case}")
    print(f"REASON={detail}")
    raise SystemExit(1)


def expected_weekly_next(now: datetime, weekdays: list[int], time_text: str, end_date: str | None = None) -> str | None:
    hour, minute = [int(x) for x in time_text.split(":", 1)]
    limit = datetime.fromisoformat(end_date + "T23:59:59+08:00").date() if end_date else None
    for offset in range(0, 370):
        day = now.date() + timedelta(days=offset)
        if day.weekday() not in weekdays:
            continue
        candidate = datetime.combine(day, dt_time(hour, minute), tzinfo=TZ)
        if candidate <= now:
            continue
        if limit and candidate.date() > limit:
            return None
        return candidate.isoformat()
    return None


def assert_no_earlier(now: datetime, expected_iso: str, weekdays: list[int], time_text: str, case: str) -> None:
    hour, minute = [int(x) for x in time_text.split(":", 1)]
    expected = datetime.fromisoformat(expected_iso).astimezone(TZ)
    probe = now + timedelta(minutes=1)
    while probe < expected:
        candidate = datetime.combine(probe.date(), dt_time(hour, minute), tzinfo=TZ)
        if now < candidate < expected and candidate.weekday() in weekdays:
            fail(case, f"earlier valid occurrence exists: {candidate.isoformat()}")
        probe += timedelta(days=1)


def assert_update_case(jobs, tools, *, case: str, now_iso: str, initial_schedule: str, update_schedule: str, end_date: str | None = None) -> None:
    fixed_now = datetime.fromisoformat(now_iso).astimezone(TZ)
    jobs._hermes_now = lambda: fixed_now
    tools._now_china = lambda: fixed_now
    created = jobs.create_job(prompt=f"Reminder: {case}", schedule=initial_schedule, name=f"TEST Generic Weekly Reminder {case}", deliver="local")
    job_id = created["id"]
    try:
        raw = tools.cronjob(action="update", job_id=job_id, schedule=update_schedule, end_date=end_date)
        data = json.loads(raw)
        if not data.get("success") or not data.get("verified"):
            fail(case, "update tool did not return success=true and verified=true")
        stored = jobs.get_job(job_id)
        if not stored:
            fail(case, "updated job missing from storage")
        schedule = stored.get("schedule") or {}
        if schedule.get("kind") != "weekly":
            fail(case, f"stored schedule is not weekly: {schedule}")
        next_run = stored.get("next_run_at")
        if not next_run:
            fail(case, "next_run_at missing after update")
        dt = datetime.fromisoformat(next_run)
        if dt.tzinfo is None or dt.astimezone(TZ).utcoffset().total_seconds() != 8 * 3600:
            fail(case, f"next_run_at not Asia/Shanghai aware: {next_run}")
        dt = dt.astimezone(TZ)
        if dt <= fixed_now:
            fail(case, f"next_run_at not future: {next_run}")
        weekdays = [int(d) for d in schedule.get("weekdays", [])]
        if dt.weekday() not in weekdays:
            fail(case, f"next_run_at weekday {dt.weekday()} not in updated weekdays {weekdays}")
        expected = expected_weekly_next(fixed_now, weekdays, schedule.get("time"), end_date)
        if next_run != expected:
            fail(case, f"expected {expected}, got {next_run}")
        assert_no_earlier(fixed_now, expected, weekdays, schedule.get("time"), case)
        lookup = load_module("hermes_reminder_lookup_test", LOOKUP_PATH)
        friendly = lookup.friendly_dt(dt)
        actual_weekday = dt.strftime("%A")
        if not friendly.startswith(actual_weekday + ","):
            fail(case, f"friendly weekday mismatch: {friendly} vs {actual_weekday}")
        print(f"{case}=PASSED")
    finally:
        jobs.remove_job(job_id)


def assert_invalid_update(jobs, tools) -> None:
    fixed_now = datetime.fromisoformat("2026-05-13T08:00:00+08:00").astimezone(TZ)
    jobs._hermes_now = lambda: fixed_now
    tools._now_china = lambda: fixed_now
    created = jobs.create_job(prompt="Reminder: invalid update test", schedule="every Monday at 09:00", name="TEST Generic Weekly Reminder invalid", deliver="local")
    try:
        raw = tools.cronjob(action="update", job_id=created["id"], schedule="every someday around tea time")
        data = json.loads(raw)
        if data.get("success") is not False:
            fail("INVALID_UPDATE", f"invalid update did not fail closed: {raw}")
        print("INVALID_UPDATE=PASSED")
    finally:
        jobs.remove_job(created["id"])


def assert_formatter_consistency() -> None:
    lookup = load_module("hermes_reminder_lookup_formatter_test", LOOKUP_PATH)
    dt = datetime.fromisoformat("2026-05-13T15:30:00+08:00").astimezone(TZ)
    friendly = lookup.friendly_dt(dt)
    if not friendly.startswith("Wednesday,"):
        fail("FORMATTER_CONSISTENCY", f"friendly formatter did not derive weekday from datetime: {friendly}")
    print("FORMATTER_CONSISTENCY=PASSED")


def load_gateway_sanitizer():
    text = GATEWAY_PATH.read_text()
    match = re.search(r"def _sanitize_user_visible_response\(text: str\) -> str:\n.*?\ndef _normalize_empty_agent_response", text, flags=re.S)
    if not match:
        fail("SANITIZER_SOURCE", "sanitize function not found")
    src = match.group(0).rsplit("\ndef _normalize_empty_agent_response", 1)[0]
    ns = {"re": re}
    exec(src, ns)
    return ns["_sanitize_user_visible_response"]


def assert_sanitizer() -> None:
    sanitize = load_gateway_sanitizer()
    raw = """cronjob([{\"action\":\"update\",\"job_id\":\"abc\",\"schedule\":\"every Tuesday at 15:30\"}])
call_ABC123
{\"success\": true, \"job_id\": \"abc\", \"deliver\": \"telegram:123456789\"}
bot12345:SECRET
api_key=SECRETKEY
Your Majesty, updated."""
    clean = sanitize(raw)
    banned = ["cronjob([", "call_", "123456789", "bot12345:", "SECRETKEY", '"success"']
    found = [b for b in banned if b in clean]
    if found:
        fail("SANITIZER", f"banned fragments leaked: {found}; output={clean}")
    print("SANITIZER=PASSED")


def main() -> int:
    jobs = load_module("cron.jobs", JOBS_PATH)
    tools = load_module("cronjob_tools_test", TOOLS_PATH)
    original_now = jobs._hermes_now
    original_tools_now = tools._now_china
    try:
        assert_update_case(jobs, tools, case="UPDATE_WEEKDAY_SET", now_iso="2026-05-13T08:00:00+08:00", initial_schedule="every Monday at 09:00", update_schedule="every Tuesday, Thursday at 15:30")
        assert_update_case(jobs, tools, case="SAME_DAY_FUTURE_AFTER_UPDATE", now_iso="2026-05-13T08:00:00+08:00", initial_schedule="every Monday at 09:00", update_schedule="every Wednesday at 15:30")
        assert_update_case(jobs, tools, case="SAME_DAY_PAST_AFTER_UPDATE", now_iso="2026-05-13T16:00:00+08:00", initial_schedule="every Monday at 09:00", update_schedule="every Wednesday at 15:30")
        assert_update_case(jobs, tools, case="MULTIDAY_WEEKLY_UPDATE", now_iso="2026-05-13T16:00:00+08:00", initial_schedule="every Monday at 09:00", update_schedule="every Wednesday, Thursday, Friday at 15:30")
        assert_update_case(jobs, tools, case="END_DATE_BOUNDARY_UPDATE", now_iso="2026-05-13T08:00:00+08:00", initial_schedule="every Monday at 09:00", update_schedule="every Wednesday at 15:30", end_date="2026-05-13")
        assert_invalid_update(jobs, tools)
        assert_formatter_consistency()
        assert_sanitizer()
        print("REMINDER_UPDATE_TEST=PASSED")
        return 0
    finally:
        jobs._hermes_now = original_now
        tools._now_china = original_tools_now
        for job in list(jobs.list_jobs(include_disabled=True)):
            if str(job.get("name") or "").startswith("TEST Generic Weekly Reminder"):
                jobs.remove_job(job["id"])


if __name__ == "__main__":
    raise SystemExit(main())
