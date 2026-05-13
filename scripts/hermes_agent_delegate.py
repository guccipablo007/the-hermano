#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE = Path("/root/.hermes")
TASK_DIR = BASE / "agent_tasks"
REPORT_DIR = TASK_DIR / "reports"
LEDGER = TASK_DIR / "tasks.jsonl"
AGENTS_DIR = BASE / "agents"

AGENTS = {
    "overseer": {
        "name": "Hermes Overseer / Main Agent",
        "route": "coordination",
        "provider": "NewCoin",
        "model": "kimi-k2.6",
    },
    "apps_coding_complex": {
        "name": "Apps, Coding & Complex Builds Agent",
        "route": "coding/debugging",
        "provider": "NewCoin",
        "model": "deepseek-v3.2",
    },
    "ops_verification": {
        "name": "Ops & Verification Agent",
        "route": "tool-first/verification",
        "provider": "NewCoin",
        "model": "qwen3-32b",
    },
    "personal_admin_tutor": {
        "name": "Personal/Admin & Tutor Agent",
        "route": "personal/admin/tutor",
        "provider": "NewCoin",
        "model": "qwen3-32b",
    },
}

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

RISKY_WORDS = [
    "delete", "remove", "drop", "reset", "wipe", "restart", "deploy", "migrate", "edit", "patch", "write",
    "configure gmail", "configure youtube", "private_data", "token", "secret", "credential",
]


def mask(text: Any) -> str:
    s = str(text)
    for pat in SECRET_PATTERNS:
        if "telegram:" in pat.pattern:
            s = pat.sub("telegram:<masked>", s)
        elif "chat_id" in pat.pattern.lower():
            s = pat.sub("chat_id=<masked>", s)
        else:
            s = pat.sub("<REDACTED>", s)
    return s


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def task_id_for(message: str) -> str:
    raw = f"{now_iso()}:{message}".encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:12]


def run_cmd(args: List[str], timeout: int = 120) -> Dict[str, Any]:
    try:
        proc = subprocess.run(args, text=True, capture_output=True, timeout=timeout)
        return {"ok": proc.returncode == 0, "rc": proc.returncode, "stdout": mask(proc.stdout), "stderr": mask(proc.stderr)}
    except Exception as exc:
        return {"ok": False, "rc": 1, "stdout": "", "stderr": f"{type(exc).__name__}:{mask(exc)}"}


def router_decision(message: str) -> Dict[str, Any]:
    script = BASE / "scripts" / "hermes_model_router.py"
    if script.exists():
        proc = run_cmd(["/usr/bin/python3", str(script), "classify", message, "--format", "raw"], timeout=60)
        try:
            data = json.loads(proc["stdout"])
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {"route": "default", "provider": "NewCoin", "model": "qwen3-32b", "reason": "fallback local classification"}


def classify(message: str) -> Dict[str, Any]:
    t = (message or "").lower()
    decision = router_decision(message)
    route = str(decision.get("route") or "default")
    tool = decision.get("tool")

    if tool in {"hermes_reminder_lookup"} or any(w in t for w in ["reminder", "schedule", "lesson plan", "student", "class", "tutor", "attendance"]):
        if any(w in t for w in ["healthy", "health", "verify", "gateway status", "backup", "provider status", "claim success", "without proof"]):
            agent_id = "ops_verification"
        else:
            agent_id = "personal_admin_tutor"
    elif tool in {"hermes_provider_status", "hermes_session_recall"} or any(w in t for w in ["healthy", "healthcheck", "gateway", "systemd", "backup", "verify", "verified", "proof", "claim success", "without proof", "provider status"]):
        agent_id = "ops_verification"
    elif route == "coding" or any(w in t for w in ["firebase", "firestore", "python", "traceback", "stack trace", "database", "app", "script", "bash", "systemd service", "code", "debug"]):
        agent_id = "apps_coding_complex"
    elif any(w in t for w in ["lesson", "student", "tutor", "class plan", "admin", "personal"]):
        agent_id = "personal_admin_tutor"
    elif route == "reasoning" and any(w in t for w in ["claim success", "proof", "verify", "hallucinate", "failure"]):
        agent_id = "ops_verification"
    elif route == "reasoning":
        agent_id = "overseer"
    else:
        agent_id = "overseer"

    agent = AGENTS[agent_id].copy()

    # Specialist assignment is authoritative for delegation display. The model
    # router decision remains useful context, but health/admin classifications
    # should not inherit a misleading coding route just because a technical word
    # such as "gateway" appears in the request.
    display_route = decision.get("route") or agent["route"]
    display_model = decision.get("model") or agent["model"]
    display_provider = decision.get("provider") or agent["provider"]
    if agent_id == "ops_verification":
        display_route = "tool-first/verification"
        display_model = "qwen3-32b" if tool or any(w in t for w in ["health", "healthy", "status", "backup", "provider", "verify", "proof"]) else display_model
    elif agent_id == "personal_admin_tutor":
        display_route = "tool-first/reminder" if tool == "hermes_reminder_lookup" else "personal/admin/tutor"
        display_model = "qwen3-32b"

    risk = "medium" if any(w in t for w in RISKY_WORDS) else "low"
    if agent_id == "apps_coding_complex" and any(w in t for w in ["fix", "patch", "edit", "write", "deploy"]):
        risk = "medium"
    if any(w in t for w in ["delete", "wipe", "reset", "drop", "credential", "token", "secret"]):
        risk = "high"

    return {
        "recommended_agent_id": agent_id,
        "recommended_agent": agent["name"],
        "route": display_route,
        "tool": tool,
        "provider": display_provider,
        "model": display_model,
        "risk_level": risk,
        "evidence_required": True,
        "reason": decision.get("reason") or "natural-language delegation classification",
    }


def ensure_dirs() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.touch(exist_ok=True)
    os.chmod(REPORT_DIR, 0o700)
    os.chmod(LEDGER, 0o600)


def write_ledger(record: Dict[str, Any]) -> None:
    ensure_dirs()
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")


def write_report(task_id: str, report: Dict[str, Any]) -> Path:
    ensure_dirs()
    path = REPORT_DIR / f"{task_id}.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    os.chmod(path, 0o600)
    return path


def safe_tool_report(task_id: str, message: str, cls: Dict[str, Any]) -> Dict[str, Any]:
    tool = cls.get("tool")
    t = message.lower()
    commands: List[str] = []
    evidence: List[Dict[str, Any]] = []
    summary = "Created bounded delegation plan."
    actions: List[str] = []
    status = "needs_user_input"

    if tool == "hermes_provider_status" or "provider status" in t or "model" in t:
        commands.append("python3 /root/.hermes/scripts/hermes_provider_status.py status --format friendly")
        proc = run_cmd(["/usr/bin/python3", "/root/.hermes/scripts/hermes_provider_status.py", "status", "--format", "friendly"])
        status = "completed" if proc["ok"] and "NewCoin" in proc["stdout"] else "failed"
        summary = "Provider/model status checked through verified local provider-status tool."
        actions.append("Ran provider-status tool.")
        evidence.append({"type": "command_contains", "command": "python3 /root/.hermes/scripts/hermes_provider_status.py status --format friendly", "contains": "NewCoin"})
    elif cls.get("recommended_agent_id") == "ops_verification" and any(w in t for w in ["health", "healthy", "gateway"]):
        commands.append("hermes_ops_healthcheck --quick")
        proc = run_cmd(["/usr/local/bin/hermes_ops_healthcheck", "--quick"], timeout=180)
        status = "completed" if proc["ok"] and "OPS_HEALTHCHECK_QUICK=PASSED" in proc["stdout"] else "failed"
        summary = "Gateway health checked through Ops Guardian quick healthcheck."
        actions.append("Ran quick Ops Guardian healthcheck.")
        evidence.append({"type": "healthcheck_quick"})
    elif cls.get("tool") == "hermes_reminder_lookup" or "reminder" in t:
        commands.append("python3 /root/.hermes/scripts/hermes_reminder_lookup.py list --format friendly")
        proc = run_cmd(["/usr/bin/python3", "/root/.hermes/scripts/hermes_reminder_lookup.py", "list", "--format", "friendly"])
        status = "completed" if proc["ok"] and "verified" in proc["stdout"].lower() else "failed"
        summary = "Reminder lookup planned or checked through storage-backed reminder lookup."
        actions.append("Used storage-backed reminder lookup route.")
        evidence.append({"type": "command_contains", "command": "python3 /root/.hermes/scripts/hermes_reminder_lookup.py list --format friendly", "contains": "verified"})
    else:
        status = "needs_user_input"
        summary = "Delegation is bounded. Specialist needs user-provided logs, code, or explicit approval before execution."
        actions.append("Classified task and prepared specialist handoff. No risky action executed.")

    return {
        "TASK_REPORT": True,
        "task_id": task_id,
        "agent": cls["recommended_agent"],
        "status": status,
        "summary": summary,
        "actions_taken": actions,
        "files_changed": [],
        "commands_run": commands,
        "tests_run": [],
        "evidence": evidence,
        "risks_or_warnings": ["Specialist report is not a final user-facing success claim."],
        "verification_recommendation": "Overseer must verify evidence before claiming success.",
        "final_answer_suggestion": "Use verified evidence only; say NOT VERIFIED if checks fail.",
    }


def verify_report(path: Path) -> Dict[str, Any]:
    proc = run_cmd(["/usr/bin/python3", str(BASE / "scripts" / "hermes_agent_report_verify.py"), str(path)], timeout=180)
    return {"verified": proc["ok"] and "VERIFIED" in proc["stdout"].splitlines()[:1], "output": proc["stdout"], "rc": proc["rc"]}


def delegate(message: str, dry_run: bool) -> Dict[str, Any]:
    ensure_dirs()
    cls = classify(message)
    task_id = task_id_for(message)
    report_path = REPORT_DIR / f"{task_id}.json"
    record = {
        "task_id": task_id,
        "timestamp": now_iso(),
        "user_intent_summary": mask(message[:240]),
        "assigned_agent": cls["recommended_agent"],
        "route": cls.get("route"),
        "provider": cls.get("provider"),
        "model": cls.get("model"),
        "status": "dry_run" if dry_run else "created",
        "risk_level": cls.get("risk_level"),
        "evidence_required": True,
        "report_path": str(report_path),
        "verification_status": "NOT_RUN" if dry_run else "PENDING",
    }

    if dry_run:
        write_ledger(record)
        return {"task_id": task_id, "mode": "dry-run", "classification": cls, "task_record": record, "execution": "NOT_EXECUTED"}

    report = safe_tool_report(task_id, message, cls)
    path = write_report(task_id, report)
    verification = verify_report(path)
    record["status"] = report["status"]
    record["verification_status"] = "VERIFIED" if verification["verified"] else "NOT VERIFIED"
    write_ledger(record)
    return {"task_id": task_id, "classification": cls, "report_path": str(path), "report": report, "verification": verification}


def status(limit: int = 10) -> List[Dict[str, Any]]:
    if not LEDGER.exists():
        return []
    rows = []
    for line in LEDGER.read_text(encoding="utf-8", errors="ignore").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def print_classification(cls: Dict[str, Any], raw: bool = False) -> None:
    if raw:
        print(json.dumps(cls, indent=2, ensure_ascii=False))
        return
    print("recommended_agent=" + cls["recommended_agent"])
    print("route=" + str(cls.get("route")))
    if cls.get("tool"):
        print("tool=" + str(cls.get("tool")))
    print("provider=" + str(cls.get("provider")))
    print("model=" + str(cls.get("model")))
    print("risk_level=" + str(cls.get("risk_level")))
    print("evidence_required=True")


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes bounded 4-agent delegation framework.")
    sub = parser.add_subparsers(dest="cmd")
    p_class = sub.add_parser("classify", help="Classify a message into one of the four agents.")
    p_class.add_argument("message")
    p_class.add_argument("--format", choices=["friendly", "raw"], default="friendly")
    p_del = sub.add_parser("delegate", help="Create a bounded task record and optional safe report.")
    p_del.add_argument("message")
    p_del.add_argument("--dry-run", action="store_true")
    p_del.add_argument("--format", choices=["friendly", "raw"], default="friendly")
    p_status = sub.add_parser("status", help="Show recent delegated task statuses.")
    p_status.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    if args.cmd == "classify":
        print_classification(classify(args.message), raw=args.format == "raw")
        return 0
    if args.cmd == "delegate":
        result = delegate(args.message, args.dry_run)
        if args.format == "raw":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            cls = result["classification"]
            print("DELEGATION_DRY_RUN=PASSED" if args.dry_run else "DELEGATION=CREATED")
            print("task_id=" + result["task_id"])
            print("assigned_agent=" + cls["recommended_agent"])
            print("route=" + str(cls.get("route")))
            print("provider=" + str(cls.get("provider")))
            print("model=" + str(cls.get("model")))
            print("risk_level=" + str(cls.get("risk_level")))
            if args.dry_run:
                print("execution=NOT_EXECUTED")
            else:
                print("report_path=" + result["report_path"])
                print("verification_status=" + ("VERIFIED" if result["verification"]["verified"] else "NOT VERIFIED"))
        return 0
    if args.cmd == "status":
        rows = status(args.limit)
        if not rows:
            print("NO_DELEGATED_TASKS_FOUND")
            return 0
        for row in rows:
            print(json.dumps({k: mask(v) for k, v in row.items()}, ensure_ascii=False, sort_keys=True))
        return 0
    parser.print_help()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
