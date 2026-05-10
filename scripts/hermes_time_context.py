#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

CHINA_TZ_NAME = "Asia/Shanghai"
CHINA_TZ = ZoneInfo(CHINA_TZ_NAME)
UTC_OFFSET_LABEL = "UTC+08:00"


def default_timezone() -> ZoneInfo:
    return CHINA_TZ


def now_china() -> datetime:
    return datetime.now(CHINA_TZ)


def format_china_time(dt: datetime | None = None) -> str:
    if dt is None:
        dt = now_china()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=CHINA_TZ)
    dt = dt.astimezone(CHINA_TZ)
    return dt.strftime("%A, %Y-%m-%d %I:%M %p China time (Asia/Shanghai, UTC+08:00)")


def parse_user_timezone_label(text: str | None) -> str:
    text_l = (text or "").lower()
    us_central_markers = [
        "u.s. central",
        "us central",
        "central time usa",
        "central time us",
        "america/chicago",
        "chicago time",
        "cdt",
    ]
    if any(marker in text_l for marker in us_central_markers):
        return "America/Chicago"
    return CHINA_TZ_NAME


def is_ambiguous_cst(text: str | None) -> bool:
    text_l = (text or "").lower()
    return "cst" in text_l and parse_user_timezone_label(text_l) == CHINA_TZ_NAME


def timezone_context_for_prompt() -> str:
    now = now_china()
    return (
        "TIMEZONE CONTEXT: The user is in China. "
        "Default all natural-language dates/times to China time "
        "(Asia/Shanghai, UTC+08:00, no DST). "
        "When the user says CST, interpret it as China Standard Time unless they explicitly say U.S. Central. "
        f"Current China time: {format_china_time(now)}."
    )


def main() -> None:
    now = now_china()
    print(timezone_context_for_prompt())
    print("CURRENT_CHINA_TIME=" + format_china_time(now))
    print("ISO_TIMESTAMP=" + now.isoformat())
    print("TIMEZONE_NAME=" + CHINA_TZ_NAME)
    print("UTC_OFFSET=+08:00")


if __name__ == "__main__":
    main()
