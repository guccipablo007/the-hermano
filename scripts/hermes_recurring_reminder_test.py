#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

JOBS_PATH = Path("/usr/local/lib/hermes-agent/cron/jobs.py")
TZ = ZoneInfo("Asia/Shanghai")


def load_jobs_module():
    sys.path.insert(0, "/usr/local/lib/hermes-agent")
    spec = importlib.util.spec_from_file_location("hermes_cron_jobs_test", JOBS_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def expect_equal(name: str, got, expected):
    if got != expected:
        print("NOT VERIFIED")
        print(f"FAILED_CASE={name}")
        print(f"EXPECTED={expected}")
        print(f"GOT={got}")
        raise SystemExit(1)
    print(f"{name}=PASSED")


def main() -> int:
    mod = load_jobs_module()
    original_now = mod._hermes_now

    def set_now(value: str):
        fixed = datetime.fromisoformat(value).astimezone(TZ)
        mod._hermes_now = lambda: fixed

    try:
        set_now("2026-05-12T23:00:00+08:00")
        expect_equal("UPLOAD_SUNDAY_6H", mod.compute_next_run(mod.parse_schedule("every Sunday at 12:00")), "2026-05-17T12:00:00+08:00")
        expect_equal("UPLOAD_SUNDAY_3H", mod.compute_next_run(mod.parse_schedule("every Sunday at 15:00")), "2026-05-17T15:00:00+08:00")
        expect_equal("UPLOAD_SUNDAY_1H", mod.compute_next_run(mod.parse_schedule("every Sunday at 17:00")), "2026-05-17T17:00:00+08:00")

        set_now("2026-05-12T08:46:00+08:00")
        tuesday = mod.parse_schedule("every Tuesday at 15:30")
        expect_equal("SAME_DAY_FUTURE_GENERIC", mod.compute_next_run(tuesday), "2026-05-12T15:30:00+08:00")

        set_now("2026-05-12T16:00:00+08:00")
        expect_equal("SAME_DAY_PAST_GENERIC", mod.compute_next_run(tuesday), "2026-05-19T15:30:00+08:00")

        schedule = mod.parse_schedule("every Tuesday, Wednesday, Thursday at 15:30")
        schedule["end_date"] = "2026-07-31"

        set_now("2026-05-12T08:46:00+08:00")
        expect_equal("MULTIDAY_SAME_DAY_FUTURE", mod.compute_next_run(schedule), "2026-05-12T15:30:00+08:00")

        set_now("2026-05-12T16:00:00+08:00")
        expect_equal("MULTIDAY_SAME_DAY_PAST", mod.compute_next_run(schedule), "2026-05-13T15:30:00+08:00")

        set_now("2026-05-13T16:00:00+08:00")
        expect_equal("MULTI_DAY_WEEKLY", mod.compute_next_run(schedule), "2026-05-14T15:30:00+08:00")

        set_now("2026-07-31T10:00:00+08:00")
        expect_equal("END_DATE_NO_FUTURE", mod.compute_next_run(schedule), None)

        set_now("2026-05-12T08:46:00+08:00")
        once = mod.parse_schedule("once at 2026-05-14 15:30")
        expect_equal("ABSOLUTE_ONCE", mod.compute_next_run(once), "2026-05-14T15:30:00+08:00")

        try:
            mod.parse_schedule("every someday around tea time")
        except ValueError:
            print("BAD_PARSE=PASSED")
        else:
            print("NOT VERIFIED")
            print("FAILED_CASE=BAD_PARSE")
            return 1

        print("RECURRING_REMINDER_TEST=PASSED")
        return 0
    finally:
        mod._hermes_now = original_now


if __name__ == "__main__":
    raise SystemExit(main())
