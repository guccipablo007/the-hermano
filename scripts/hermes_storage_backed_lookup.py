#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any, Iterable, List


def resolve_base() -> Path:
    env_base = os.environ.get("HERMES_BASE", "").strip()
    if env_base:
        return Path(env_base)
    live = Path("/root/.hermes")
    if live.exists():
        return live
    return Path(__file__).resolve().parents[1]


BASE = resolve_base()
DEFAULT_STORAGE = [
    Path(os.environ.get("HERMES_REMINDER_STORAGE", "")).expanduser() if os.environ.get("HERMES_REMINDER_STORAGE") else None,
    BASE / "cron" / "jobs.json",
    BASE / "storage" / "reminders.json",
]


def load_rows() -> List[dict[str, Any]]:
    for candidate in DEFAULT_STORAGE:
        if not candidate:
            continue
        if candidate.exists():
            data = json.loads(candidate.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [row for row in data if isinstance(row, dict)]
            if isinstance(data, dict):
                for key in ("jobs", "reminders", "items"):
                    if isinstance(data.get(key), list):
                        return [row for row in data[key] if isinstance(row, dict)]
    return []


def as_text(row: dict[str, Any]) -> str:
    values: Iterable[Any] = [
        row.get("name"),
        row.get("title"),
        row.get("prompt"),
        row.get("task"),
        row.get("category"),
        row.get("type"),
        " ".join(map(str, row.get("tags") or [])),
    ]
    return " ".join(str(value or "") for value in values).strip()


def active_rows(rows: List[dict[str, Any]]) -> List[dict[str, Any]]:
    active = []
    for row in rows:
        status = str(row.get("status") or row.get("state") or "active").lower()
        if status in {"deleted", "removed", "cancelled", "canceled", "done", "completed", "error", "failed"}:
            continue
        active.append(row)
    return active


def render(kind: str, rows: List[dict[str, Any]]) -> dict[str, Any]:
    verified = active_rows(rows)
    return {
        "kind": kind,
        "verification_status": "VERIFIED" if verified else "NOT VERIFIED",
        "verified": bool(verified),
        "rows": verified,
        "summary": f"{kind.replace('-', ' ').title()} loaded from storage." if verified else f"{kind.replace('-', ' ').title()} is not verified in storage.",
    }


def print_friendly(data: dict[str, Any]) -> None:
    if not data["verified"]:
        print("NOT VERIFIED")
        print(f"REASON={data['kind'].upper().replace('-', '_')}_NOT_FOUND_IN_STORAGE")
        return
    print("VERIFIED_STORAGE_LOOKUP=PASSED")
    print(f"KIND={data['kind']}")
    print(f"RESULT_COUNT={len(data['rows'])}")
    print(f"SUMMARY={data['summary']}")
    for idx, row in enumerate(data["rows"], 1):
        schedule = row.get("next_run_at") or row.get("schedule") or row.get("rrule") or "NOT VERIFIED"
        title = row.get("name") or row.get("title") or row.get("prompt") or "Stored reminder"
        status = row.get("status") or row.get("state") or "unknown"
        print(f"{idx}. {title}")
        print(f"   schedule={schedule}")
        print(f"   status={status}")


def upload_schedule(rows: List[dict[str, Any]]) -> List[dict[str, Any]]:
    matches = []
    for row in active_rows(rows):
        text = as_text(row).lower()
        if "upload" in text:
            matches.append(row)
    return matches


def any_reminders(rows: List[dict[str, Any]]) -> List[dict[str, Any]]:
    return active_rows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Storage-backed reminder and upload schedule lookup.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("upload-schedule", "any-reminders"):
        p = sub.add_parser(name)
        p.add_argument("--format", choices=["friendly", "json"], default="friendly")
    args = parser.parse_args()

    rows = load_rows()
    selected = upload_schedule(rows) if args.cmd == "upload-schedule" else any_reminders(rows)
    data = render(args.cmd, selected)
    if args.format == "json":
        print(json.dumps(data, ensure_ascii=False))
    else:
        print_friendly(data)
    return 0 if data["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
