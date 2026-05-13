#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

LOOKUP = Path("/root/.hermes/scripts/hermes_reminder_lookup.py")
RAW_CRON_RE = re.compile(r"\b[\d*/,-]+\s+[\d*/,-]+\s+[\d*/,-]+\s+[\d*/,-]+\s+[\d*/,-]+\b")


def load_lookup():
    spec = importlib.util.spec_from_file_location("hermes_reminder_lookup_format", LOOKUP)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def fail(case: str, reason: str) -> None:
    print("NOT VERIFIED")
    print(f"FAILED_CASE={case}")
    print(f"REASON={reason}")
    raise SystemExit(1)


def job(expr: str) -> dict:
    return {"schedule": {"kind": "cron", "expr": expr}, "schedule_display": expr}


def expect(case: str, got: str, expected: str) -> None:
    if got != expected:
        fail(case, f"expected {expected!r}, got {got!r}")
    print(f"{case}=PASSED")


def main() -> int:
    mod = load_lookup()
    expect("DAILY_CRON_FRIENDLY", mod.friendly_schedule(job("0 7 * * *")), "Every day at 7:00 AM.")
    expect("WEEKLY_SATURDAY_CRON_FRIENDLY", mod.friendly_schedule(job("30 10 * * 6")), "Every Saturday at 10:30 AM.")
    expect("WEEKLY_SUNDAY_NOON_CRON_FRIENDLY", mod.friendly_schedule(job("0 12 * * 0")), "Every Sunday at 12:00 PM.")
    expect("WEEKLY_SUNDAY_AFTERNOON_CRON_FRIENDLY", mod.friendly_schedule(job("0 15 * * 0")), "Every Sunday at 3:00 PM.")
    expect("WEEKLY_SUNDAY_5PM_CRON_FRIENDLY", mod.friendly_schedule(job("0 17 * * 0")), "Every Sunday at 5:00 PM.")
    unsupported = mod.friendly_schedule(job("*/15 9-17 * * 1-5"))
    expect("UNSUPPORTED_CRON_HIDDEN", unsupported, "Verified schedule from storage.")
    raw = mod.schedule_text(job("*/15 9-17 * * 1-5"))
    if raw != "*/15 9-17 * * 1-5":
        fail("RAW_MODE_PRESERVED", f"raw schedule changed: {raw}")
    print("RAW_MODE_PRESERVED=PASSED")
    friendly_text = "\n".join([
        mod.friendly_schedule(job("0 7 * * *")),
        mod.friendly_schedule(job("30 10 * * 6")),
        unsupported,
    ])
    if RAW_CRON_RE.search(friendly_text):
        fail("FRIENDLY_NO_RAW_CRON", friendly_text)
    print("FRIENDLY_NO_RAW_CRON=PASSED")
    print("REMINDER_LOOKUP_FORMAT_TEST=PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
