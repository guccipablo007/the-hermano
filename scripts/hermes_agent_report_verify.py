#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

SECRET_PATTERNS = [
    re.compile(r"bot\d+:[A-Za-z0-9_-]+"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]+", re.I),
    re.compile(r"sk-[A-Za-z0-9_-]+"),
    re.compile(r"ghp_[A-Za-z0-9_]+"),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"(?i)(api[_-]?key|token|secret|password|authorization|oauth)[=:]\s*[^\s,]+"),
    re.compile(r"telegram:([-]?\d{6,})"),
    re.compile(r"(?i)chat_id[=: ]+[-]?\d{6,}"),
]

VALID_STATUSES = {"completed", "blocked", "failed", "needs_user_input"}


def mask(text: Any) -> str:
    s = str(text)
    for pat in SECRET_PATTERNS:
        if "telegram:" in pat.pattern:
            s = pat.sub("telegram:<masked>", s)
        elif "chat_id" in pat.pattern.lower():
            s = pat.sub("chat_id=<masked>", s)
        else:
            s = pat.sub(lambda m: m.group(0).split("=", 1)[0] + "=<REDACTED>" if "=" in m.group(0) else "<REDACTED>", s)
    return s


def load_report(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    stripped = text.strip()
    if stripped.startswith("{"):
        return json.loads(stripped)
    data: Dict[str, Any] = {}
    current_key = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.strip() == "TASK_REPORT":
            continue
        if ":" in line and not line.startswith((" ", "-", "\t")):
            key, value = line.split(":", 1)
            current_key = key.strip()
            data[current_key] = value.strip()
        elif current_key:
            data[current_key] = str(data.get(current_key, "")) + "\n" + line
    return data


def normalize_evidence(value: Any) -> List[Any]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [value]
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return []
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict):
                return [parsed]
        except Exception:
            pass
        return [line.strip(" -") for line in s.splitlines() if line.strip(" -")]
    return [value]


def run_command(cmd: str, timeout: int = 120) -> Tuple[bool, str]:
    try:
        proc = subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=timeout)
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode == 0, mask(out[-2000:])
    except Exception as exc:
        return False, f"{type(exc).__name__}:{mask(exc)}"


def verify_evidence_item(item: Any) -> Tuple[bool, str]:
    if isinstance(item, str):
        low = item.lower()
        if "verified" in low or "passed" in low or "ops_healthcheck" in low or "commit" in low:
            return True, mask(item[:300])
        return False, "plain evidence lacks verifiable pass marker"
    if not isinstance(item, dict):
        return False, "unsupported evidence item"
    etype = str(item.get("type") or item.get("kind") or "").strip()
    if etype == "file_exists":
        path = Path(str(item.get("path") or ""))
        ok = path.exists() and (not path.is_file() or path.stat().st_size > 0)
        return ok, f"file_exists {path}: {'ok' if ok else 'missing_or_empty'}"
    if etype == "service_active":
        service = str(item.get("service") or "")
        ok, out = run_command(f"systemctl is-active {service}")
        return ok and "active" in out, f"service_active {service}: {out.strip()}"
    if etype == "command_contains":
        cmd = str(item.get("command") or "")
        expected = str(item.get("contains") or "")
        ok, out = run_command(cmd)
        return ok and expected in out, f"command_contains expected={expected!r}: {'matched' if expected in out else 'not_matched'}"
    if etype == "latest_backup":
        ok, out = run_command("cd /root/hermano-backup && git rev-parse HEAD")
        return ok and bool(re.search(r"[0-9a-f]{40}", out)), "latest_backup commit verified" if ok else out
    if etype == "healthcheck_quick":
        ok, out = run_command("hermes_ops_healthcheck --quick")
        return ok and "OPS_HEALTHCHECK_QUICK=PASSED" in out, "quick healthcheck passed" if ok else out
    return False, f"unknown evidence type: {mask(etype)}"


def verify_report(path: Path) -> Tuple[bool, List[str]]:
    messages: List[str] = []
    if not path.exists() or path.stat().st_size == 0:
        return False, ["report missing or empty"]
    try:
        data = load_report(path)
    except Exception as exc:
        return False, [f"report parse failed: {type(exc).__name__}:{mask(exc)}"]
    status = str(data.get("status") or "").strip()
    if status not in VALID_STATUSES:
        messages.append(f"invalid status: {mask(status)}")
    evidence = normalize_evidence(data.get("evidence"))
    if status == "completed" and not evidence:
        messages.append("completed report has no evidence")
    verified_count = 0
    for item in evidence:
        ok, msg = verify_evidence_item(item)
        messages.append(("OK " if ok else "FAIL ") + msg)
        if ok:
            verified_count += 1
    if status == "completed" and verified_count == 0:
        messages.append("no verifiable evidence succeeded")
    safe = not any(m.startswith("invalid status") or m.startswith("completed report has no evidence") or m.startswith("FAIL") or m.startswith("no verifiable") for m in messages)
    if status in {"blocked", "failed", "needs_user_input"}:
        safe = status in VALID_STATUSES and bool(data.get("summary") or data.get("risks_or_warnings") or data.get("verification_recommendation"))
    return safe, messages


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Hermes specialist task reports before Overseer user-facing claims.")
    parser.add_argument("report", nargs="?", help="Path to specialist report JSON/text")
    parser.add_argument("--format", choices=["friendly", "raw"], default="friendly")
    args = parser.parse_args()
    if not args.report:
        parser.print_help()
        return 0
    ok, messages = verify_report(Path(args.report))
    print("VERIFIED" if ok else "NOT VERIFIED")
    for msg in messages[:20]:
        print(mask(msg))
    return 0 if ok else 2

if __name__ == "__main__":
    raise SystemExit(main())
