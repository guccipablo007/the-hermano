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
from zoneinfo import ZoneInfo

BASE = Path("/root/.hermes")
TASK_DIR = BASE / "agent_tasks"
REPORT_DIR = TASK_DIR / "reports"
LEDGER = TASK_DIR / "tasks.jsonl"
AGENTS_DIR = BASE / "agents"
CHINA_TZ = ZoneInfo("Asia/Shanghai")

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
    if agent_id == "apps_coding_complex":
        display_route = "coding/debugging"
        display_model = "deepseek-v3.2"
    elif agent_id == "ops_verification":
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



def dry_run_blueprint(message: str, cls: Dict[str, Any]) -> Dict[str, Any]:
    agent_id = cls.get("recommended_agent_id") or "overseer"
    low = (message or "").lower()
    common_prohibited = [
        "No commands executed.",
        "No files edited.",
        "No services restarted.",
        "No reminders created, changed, or deleted.",
        "No destructive tools called.",
    ]
    if agent_id == "apps_coding_complex":
        return {
            "summary": "Dry-run plan for an app/coding/debugging task.",
            "why_this_agent": "The request involves app, Firebase, Firestore, code, logs, or debugging work.",
            "proposed_steps": [
                "Collect the exact error message, logs, and smallest relevant code/config snippet.",
                "Identify the failing layer: client code, Firebase rules, SDK initialization, network/auth, or Firestore write path.",
                "Inspect only credential-free configuration and code paths provided by the user.",
                "Propose a minimal patch and verification commands after evidence is available.",
            ],
            "required_user_inputs": ["Exact error/log output", "Relevant code snippet", "Firebase/Firestore config shape with credentials removed", "What action should trigger the write"],
            "evidence_needed_before_success": ["Reproduced error or log", "Patch diff if execution is later allowed", "Passing verification command or confirmed app behavior"],
            "risks_or_warnings": ["Do not inspect credentials or service-account private values.", "Do not edit files until execution is explicitly enabled."],
            "actions_not_taken": common_prohibited,
        }
    if agent_id == "ops_verification":
        return {
            "summary": "Dry-run plan for Ops and Verification work.",
            "why_this_agent": "The request asks for health, provider, gateway, backup, log, or verification evidence.",
            "proposed_steps": [
                "Run read-only status checks when execution is later allowed.",
                "Inspect healthcheck output, systemd status, recent logs, and verified records.",
                "Compare claims against tool output or stored evidence.",
                "Return VERIFIED or NOT VERIFIED with concise evidence.",
            ],
            "required_user_inputs": ["Scope of verification", "Whether read-only checks are allowed", "Relevant time window if checking logs"],
            "evidence_needed_before_success": ["Healthcheck pass marker", "systemctl active status", "log excerpt or stored verification record", "backup commit hash if backup-related"],
            "risks_or_warnings": ["Dry-run does not restart services.", "Dry-run does not change gateway state."],
            "actions_not_taken": common_prohibited,
        }
    if agent_id == "personal_admin_tutor":
        return {
            "summary": "Dry-run plan for personal/admin/tutor work.",
            "why_this_agent": "The request involves reminders, schedules, lesson planning, student/class admin, or tutoring work.",
            "proposed_steps": [
                "For reminders, query verified storage first and apply the query-first guard for ambiguous phrasing.",
                "Ask for missing date/time/task before any reminder creation.",
                "For lesson/admin tasks, gather topic, student level, format, and output requirements.",
                "Only create files or reminders after explicit execution is enabled and verification requirements are met.",
            ],
            "required_user_inputs": ["For reminders: task, date/relative date, time/offset", "For lessons: topic, age/level, format, and length"],
            "evidence_needed_before_success": ["Storage-backed reminder record after creation", "File existence/media verification for generated lesson artifacts"],
            "risks_or_warnings": ["No reminder is created in dry-run.", "No schedule is guessed from memory."],
            "actions_not_taken": common_prohibited,
        }
    return {
        "summary": "Dry-run plan for Overseer coordination.",
        "why_this_agent": "The request needs coordination, routing, or clarification before specialist work.",
        "proposed_steps": ["Clarify intent", "Select specialist if needed", "Define evidence requirements", "Avoid success claims without verification"],
        "required_user_inputs": ["Clarify the desired outcome"],
        "evidence_needed_before_success": ["Tool output, file check, service status, or stored verification record"],
        "risks_or_warnings": ["No specialist execution occurred."],
        "actions_not_taken": common_prohibited,
    }


def dry_run_report(task_id: str, message: str, cls: Dict[str, Any]) -> Dict[str, Any]:
    bp = dry_run_blueprint(message, cls)
    return {
        "DRY_RUN_DELEGATION_PLAN": True,
        "TASK_REPORT": True,
        "task_id": task_id,
        "dry_run": True,
        "assigned_agent": cls["recommended_agent"],
        "agent": cls["recommended_agent"],
        "route": cls.get("route"),
        "provider": cls.get("provider"),
        "model": cls.get("model"),
        "status": "planned",
        "summary": bp["summary"],
        "why_this_agent": bp["why_this_agent"],
        "proposed_steps": bp["proposed_steps"],
        "required_user_inputs": bp["required_user_inputs"],
        "evidence_needed_before_success": bp["evidence_needed_before_success"],
        "risks_or_warnings": bp["risks_or_warnings"],
        "actions_not_taken": bp["actions_not_taken"],
        "actions_taken": ["Classified request", "Created dry-run task ledger entry", "Created dry-run report"],
        "files_changed": [],
        "commands_run": [],
        "tests_run": [],
        "evidence": [],
        "verification_status": "NOT_EXECUTED_DRY_RUN",
        "verification_recommendation": "Dry-run only. Do not claim execution success.",
        "final_answer_suggestion": "Present the plan and request missing inputs; do not claim completion.",
    }


def format_dry_run_response(report: Dict[str, Any]) -> str:
    lines = [
        "DRY_RUN_DELEGATION_PLAN=CREATED",
        "task_id=" + str(report.get("task_id")),
        "assigned_agent=" + str(report.get("assigned_agent")),
        "route=" + str(report.get("route")),
        "provider=" + str(report.get("provider")),
        "model=" + str(report.get("model")),
        "verification_status=NOT_EXECUTED_DRY_RUN",
        "",
        "summary=" + str(report.get("summary")),
        "why_this_agent=" + str(report.get("why_this_agent")),
        "required_user_inputs=" + "; ".join(map(str, report.get("required_user_inputs") or [])),
        "proposed_actions=" + "; ".join(map(str, report.get("proposed_steps") or [])),
        "prohibited_actions=" + "; ".join(map(str, report.get("actions_not_taken") or [])),
    ]
    return "\n".join(lines)

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
        report = dry_run_report(task_id, message, cls)
        path = write_report(task_id, report)
        record.update({
            "dry_run": True,
            "status": "planned",
            "required_user_inputs": report.get("required_user_inputs", []),
            "proposed_actions": report.get("proposed_steps", []),
            "prohibited_actions": report.get("actions_not_taken", []),
            "verification_status": "NOT_EXECUTED_DRY_RUN",
            "report_path": str(path),
        })
        write_ledger(record)
        return {"task_id": task_id, "mode": "dry-run", "classification": cls, "task_record": record, "report_path": str(path), "report": report, "execution": "NOT_EXECUTED"}

    report = safe_tool_report(task_id, message, cls)
    path = write_report(task_id, report)
    verification = verify_report(path)
    record["status"] = report["status"]
    record["verification_status"] = "VERIFIED" if verification["verified"] else "NOT VERIFIED"
    write_ledger(record)
    return {"task_id": task_id, "classification": cls, "report_path": str(path), "report": report, "verification": verification}



BLOCKED_RISKY_PATTERNS = [
    r"\brestart\b", r"\bfix\b", r"\bpatch\b", r"\bedit\b", r"\bwrite\b", r"\bdelete\b",
    r"\bcreate\s+(a\s+)?reminder\b", r"\bupdate\s+(a\s+)?reminder\b", r"\bdelete\s+(a\s+)?reminder\b",
    r"\binstall\b", r"\bdeploy\b", r"\bmigrate\b", r"\bdatabase\s+write\b", r"\bconfigure\b",
]

LOW_RISK_APPROVAL_PHRASE = "YES, EXECUTE LOW-RISK WRITE"
LOW_RISK_BLOCKED_PATTERNS = [
    r"\brestart\b", r"\bfix\b", r"\bpatch\b", r"\bedit\b", r"\bdelete\b", r"\bremove\b",
    r"\binstall\b", r"\bdeploy\b", r"\bmigrate\b", r"\bdatabase\b", r"\bconfigure\b",
    r"\bconfig\.yaml\b", r"\bmodel\s+routing\b", r"\bprovider\s+routing\b",
    r"\bgmail\b", r"\byoutube\b", r"\bcredential\b", r"\btoken\b", r"\bsecret\b",
]
REMINDER_CREATE_RE = re.compile(r"\b(remind\s+me|set\s+a\s+reminder|create\s+a\s+reminder)\b", re.I)
REMINDER_UPDATE_RE = re.compile(r"\bupdate\b.*\breminder\b|\breminder\b.*\bupdate\b", re.I)
REMINDER_DELETE_RE = re.compile(r"\b(delete|remove|cancel)\b.*\b(reminder|alert)\b|\b(reminder|alert)\b.*\b(delete|remove|cancel)\b", re.I)
TASK_NOTE_RE = re.compile(r"\b(create|save|add)\b.*\b(task\s+note|agent\s+note|task\s+report|note/report|report)\b", re.I)


def readonly_plan(message: str) -> Dict[str, Any]:
    t = (message or "").lower()
    if any(re.search(pat, t) for pat in BLOCKED_RISKY_PATTERNS):
        return {"allowed": False, "kind": "blocked", "reason": "BLOCKED_RISKY_ACTION"}
    if "deep" in t and ("healthcheck" in t or "health check" in t):
        return {"allowed": True, "kind": "deep_healthcheck", "args": ["/usr/local/bin/hermes_ops_healthcheck", "--deep"], "contains": "OPS_HEALTHCHECK_DEEP=PASSED", "summary": "Deep Ops Guardian healthcheck completed."}
    if "quick" in t and ("healthcheck" in t or "health check" in t):
        return {"allowed": True, "kind": "quick_healthcheck", "args": ["/usr/local/bin/hermes_ops_healthcheck", "--quick"], "contains": "OPS_HEALTHCHECK_QUICK=PASSED", "summary": "Quick Ops Guardian healthcheck completed."}
    if "gateway" in t and any(w in t for w in ["health", "healthy", "status", "check"]):
        return {"allowed": True, "kind": "gateway_active", "args": ["/bin/systemctl", "is-active", "hermes-gateway.service"], "contains": "active", "summary": "Hermes gateway service status checked."}
    if "provider" in t or "model" in t:
        return {"allowed": True, "kind": "provider_status", "args": ["/usr/bin/python3", "/root/.hermes/scripts/hermes_provider_status.py", "status", "--format", "friendly"], "contains": "NewCoin", "summary": "Provider/model status checked."}
    if "delegated" in t or "task ledger" in t or "agent tasks" in t:
        return {"allowed": True, "kind": "delegated_task_status", "args": ["/usr/bin/python3", "/root/.hermes/scripts/hermes_agent_delegate.py", "status", "--format", "friendly", "--limit", "8"], "contains": "Recent delegated tasks", "summary": "Recent delegated task ledger read."}
    if "reminder" in t or "reminders" in t or "alerts" in t:
        return {"allowed": True, "kind": "reminder_lookup", "args": ["/usr/bin/python3", "/root/.hermes/scripts/hermes_reminder_lookup.py", "list", "--format", "friendly"], "contains": "verified", "summary": "Reminder list read from storage."}
    if "latest" in t and "backup" in t:
        return {"allowed": True, "kind": "latest_backup", "args": ["/usr/bin/python3", "/root/.hermes/scripts/hermes_verify_claim.py", "latest-backup"], "contains": "VERIFIED", "summary": "Latest Git backup commit verified."}
    if "route" in t and "audit" in t:
        return {"allowed": True, "kind": "route_audit", "args": ["/usr/bin/tail", "-20", "/root/.hermes/model_routing/live_route_audit.jsonl"], "contains": "route", "summary": "Recent route-audit entries inspected."}
    return {"allowed": False, "kind": "blocked", "reason": "NOT_READ_ONLY_WHITELISTED"}


def readonly_report(task_id: str, message: str, cls: Dict[str, Any], plan: Dict[str, Any], proc: Dict[str, Any] | None) -> Dict[str, Any]:
    blocked = not plan.get("allowed")
    ok = bool(proc and proc.get("ok") and str(plan.get("contains") or "") in (proc.get("stdout", "") + proc.get("stderr", "")))
    status = "blocked" if blocked else ("completed" if ok else "failed")
    verification_status = "BLOCKED_RISKY_ACTION" if blocked and plan.get("reason") == "BLOCKED_RISKY_ACTION" else ("NOT VERIFIED" if blocked else ("VERIFIED" if ok else "FAILED"))
    command_label = " ".join(plan.get("args") or []) if plan.get("args") else "NONE_BLOCKED"
    evidence = [] if blocked else [{"type": "command_contains", "command": command_label, "contains": plan.get("contains", "")}]
    return {
        "READ_ONLY_EXECUTION_REPORT": True,
        "TASK_REPORT": True,
        "task_id": task_id,
        "assigned_agent": cls["recommended_agent"],
        "agent": cls["recommended_agent"],
        "route": cls.get("route"),
        "provider": cls.get("provider"),
        "model": cls.get("model"),
        "status": status,
        "read_only": True,
        "read_only_kind": plan.get("kind"),
        "command_or_tool_used": command_label,
        "summary": plan.get("summary") or plan.get("reason") or "Read-only execution blocked or unavailable.",
        "evidence": evidence,
        "command_output_excerpt": mask(((proc or {}).get("stdout", "") + "\n" + (proc or {}).get("stderr", ""))[:3000]),
        "verification_status": verification_status,
        "actions_not_taken": ["No file edits.", "No service restarts.", "No package installs.", "No database writes.", "No reminder create/update/delete.", "No arbitrary shell execution."],
        "risks_or_warnings": ["Read-only whitelist enforced."] if not blocked else ["Request was not allowed by read-only whitelist."],
        "verification_recommendation": "Use report verification before claiming success.",
        "final_answer_suggestion": "Return concise evidence and verification status.",
    }


def execute_readonly(message: str) -> Dict[str, Any]:
    ensure_dirs()
    cls = classify(message)
    task_id = task_id_for("readonly:" + message)
    plan = readonly_plan(message)
    proc = run_cmd(plan["args"], timeout=300) if plan.get("allowed") else None
    report = readonly_report(task_id, message, cls, plan, proc)
    path = write_report(task_id, report)
    record = {
        "task_id": task_id,
        "timestamp": now_iso(),
        "user_intent_summary": mask(message[:240]),
        "assigned_agent": cls["recommended_agent"],
        "route": cls.get("route"),
        "provider": cls.get("provider"),
        "model": cls.get("model"),
        "status": report["status"],
        "risk_level": cls.get("risk_level"),
        "read_only": True,
        "evidence_required": True,
        "report_path": str(path),
        "verification_status": report["verification_status"],
    }
    write_ledger(record)
    return {"task_id": task_id, "classification": cls, "report_path": str(path), "report": report}


def format_readonly_response(result: Dict[str, Any]) -> str:
    report = result["report"]
    if report.get("read_only_kind") == "delegated_task_status":
        excerpt = str(report.get("command_output_excerpt") or "").strip()
        return "\n".join([
            "READ_ONLY_EXECUTION_REPORT=CREATED",
            "task_id=" + str(result.get("task_id")),
            "assigned_agent=" + str(report.get("assigned_agent")),
            "status=" + str(report.get("status")),
            "verification_status=" + str(report.get("verification_status")),
            "summary=" + str(report.get("summary")),
            "",
            excerpt,
            "",
            "No files, services, reminders, packages, databases, or provider settings were changed.",
        ]).strip()
    lines = [
        "READ_ONLY_EXECUTION_REPORT=CREATED",
        "task_id=" + str(result.get("task_id")),
        "assigned_agent=" + str(report.get("assigned_agent")),
        "route=" + str(report.get("route")),
        "provider=" + str(report.get("provider")),
        "model=" + str(report.get("model")),
        "status=" + str(report.get("status")),
        "verification_status=" + str(report.get("verification_status")),
        "read_only=true",
        "command_or_tool_used=" + str(report.get("command_or_tool_used")),
        "summary=" + str(report.get("summary")),
    ]
    if report.get("command_output_excerpt"):
        lines.append("evidence=" + str(report.get("command_output_excerpt")).replace("\n", " | ")[:1200])
    lines.append("actions_not_taken=" + "; ".join(map(str, report.get("actions_not_taken") or [])))
    return "\n".join(lines)


def reminder_guard_json(message: str) -> Dict[str, Any]:
    proc = run_cmd(["/usr/bin/python3", "/root/.hermes/scripts/hermes_reminder_intent_guard.py", message or "", "--format", "json"], timeout=60)
    if not proc.get("ok"):
        return {"applies": False, "create_allowed": False, "direct_response": False, "category": "guard_failed", "response": proc.get("stderr") or proc.get("stdout")}
    try:
        data = json.loads(proc.get("stdout") or "{}")
        return data if isinstance(data, dict) else {"applies": False, "create_allowed": False, "category": "guard_bad_json"}
    except Exception:
        return {"applies": False, "create_allowed": False, "category": "guard_parse_failed"}


def low_risk_block_reason(message: str) -> str | None:
    text = message or ""
    low = text.lower()
    if REMINDER_DELETE_RE.search(text):
        return "Reminder deletion is not allowed in this phase."
    for pat in LOW_RISK_BLOCKED_PATTERNS:
        if re.search(pat, low):
            # Reminder creation and approved task-note writes are handled by narrow allow-list paths below.
            if REMINDER_CREATE_RE.search(text) and not re.search(r"\b(delete|remove|cancel)\b", low):
                continue
            if TASK_NOTE_RE.search(text) and not any(x in low for x in ["config", "code", "provider", "model routing", "credential", "token", "secret"]):
                continue
            return "Request is outside the low-risk write allow-list."
    return None


def parse_reminder_create(message: str) -> Dict[str, str] | None:
    text = re.sub(r"^\s*YES,\s*EXECUTE\s+LOW-RISK\s+WRITE\s*:\s*", "", message or "", flags=re.I).strip()
    m = re.search(r"\bremind\s+me\s+(.+?)\s+to\s+(.+)$", text, re.I)
    if not m:
        m = re.search(r"\b(?:set|create)\s+a\s+reminder\s+(.+?)\s+to\s+(.+)$", text, re.I)
    if not m:
        return None
    schedule = m.group(1).strip()
    task = m.group(2).strip().rstrip(".")
    if not schedule or not task:
        return None
    return {
        "schedule": schedule,
        "task": task,
        "name": f"Reminder: {task[:80]}",
        "prompt": f"Reminder: {task}",
    }


def create_verified_reminder(message: str) -> Dict[str, Any]:
    guard = reminder_guard_json(message)
    if not guard.get("create_allowed"):
        return {
            "status": "blocked",
            "verification_status": "NOT VERIFIED",
            "write_type": "reminder_create",
            "summary": str(guard.get("response") or "Reminder request is missing required task/date/time details."),
            "evidence": [{"type": "reminder_intent_guard", "category": guard.get("category"), "create_allowed": False}],
        }
    parsed = parse_reminder_create(message)
    if not parsed:
        return {
            "status": "blocked",
            "verification_status": "NOT VERIFIED",
            "write_type": "reminder_create",
            "summary": "Could not deterministically extract reminder schedule and task.",
            "evidence": [{"type": "reminder_intent_guard", "category": guard.get("category"), "create_allowed": True}],
        }
    try:
        sys.path.insert(0, "/usr/local/lib/hermes-agent")
        from tools.cronjob_tools import cronjob  # type: ignore

        raw = cronjob(
            action="create",
            prompt=parsed["prompt"],
            schedule=parsed["schedule"],
            name=parsed["name"],
            deliver="local",
        )
        data = json.loads(raw)
    except Exception as exc:
        return {
            "status": "failed",
            "verification_status": "FAILED",
            "write_type": "reminder_create",
            "summary": f"Reminder create tool failed: {type(exc).__name__}",
            "evidence": [{"type": "exception", "detail": mask(exc)}],
        }
    job = data.get("job") or {}
    verified = bool(data.get("success") and data.get("verified") and job.get("job_id") and job.get("next_run_at"))
    return {
        "status": "completed" if verified else "failed",
        "verification_status": "VERIFIED" if verified else "NOT VERIFIED",
        "write_type": "reminder_create",
        "summary": "Reminder created through the verified cronjob flow." if verified else "Reminder creation was not verified from storage.",
        "reminder_job_id": job.get("job_id"),
        "next_run_at": job.get("next_run_at"),
        "evidence": [{"type": "cronjob_create", "success": data.get("success"), "verified": data.get("verified"), "job_id": job.get("job_id"), "next_run_at": job.get("next_run_at")}],
    }


def parse_reminder_update(message: str) -> Dict[str, str] | None:
    text = re.sub(r"^\s*YES,\s*EXECUTE\s+LOW-RISK\s+WRITE\s*:\s*", "", message or "", flags=re.I).strip()
    job_match = re.search(r"\b([0-9a-f]{12})\b", text, re.I)
    sched_match = re.search(r"\bto\s+(.+)$", text, re.I)
    if not job_match or not sched_match:
        return None
    schedule = sched_match.group(1).strip().rstrip(".")
    if not schedule:
        return None
    return {"job_id": job_match.group(1).lower(), "schedule": schedule}


def update_verified_reminder(message: str) -> Dict[str, Any]:
    parsed = parse_reminder_update(message)
    if not parsed:
        return {
            "status": "blocked",
            "verification_status": "NOT VERIFIED",
            "write_type": "reminder_update",
            "summary": "Reminder update requires an explicit existing job ID and a new schedule.",
            "evidence": [{"type": "update_validation", "job_id_present": False}],
        }
    try:
        sys.path.insert(0, "/usr/local/lib/hermes-agent")
        from tools.cronjob_tools import cronjob  # type: ignore

        raw = cronjob(action="update", job_id=parsed["job_id"], schedule=parsed["schedule"])
        data = json.loads(raw)
    except Exception as exc:
        return {
            "status": "failed",
            "verification_status": "FAILED",
            "write_type": "reminder_update",
            "summary": f"Reminder update tool failed: {type(exc).__name__}",
            "evidence": [{"type": "exception", "detail": mask(exc)}],
        }
    job = data.get("job") or {}
    verified = bool(data.get("success") and data.get("verified") and job.get("job_id") and job.get("next_run_at"))
    return {
        "status": "completed" if verified else "failed",
        "verification_status": "VERIFIED" if verified else "NOT VERIFIED",
        "write_type": "reminder_update",
        "summary": "Reminder updated through the verified cronjob flow." if verified else "Reminder update was not verified from storage.",
        "reminder_job_id": job.get("job_id") or parsed["job_id"],
        "next_run_at": job.get("next_run_at"),
        "evidence": [{"type": "cronjob_update", "success": data.get("success"), "verified": data.get("verified"), "job_id": job.get("job_id") or parsed["job_id"], "next_run_at": job.get("next_run_at")}],
    }


def task_note_body(message: str, task_id: str, cls: Dict[str, Any]) -> Dict[str, Any]:
    clean = re.sub(r"^\s*YES,\s*EXECUTE\s+LOW-RISK\s+WRITE\s*:\s*", "", message or "", flags=re.I).strip()
    return {
        "TASK_NOTE": True,
        "task_id": task_id,
        "timestamp": now_iso(),
        "summary": mask(clean[:500]),
        "assigned_agent": cls["recommended_agent"],
        "route": cls.get("route"),
        "provider": cls.get("provider"),
        "model": cls.get("model"),
        "non_sensitive": True,
        "actions_taken": ["Created a non-sensitive task note under the approved Hermes agent_tasks/reports directory."],
        "actions_not_taken": ["No code/config edited.", "No services restarted.", "No packages installed.", "No provider/model routing changed.", "No reminders changed."],
    }


def low_risk_write_action(message: str, cls: Dict[str, Any], task_id: str) -> Dict[str, Any]:
    block_reason = low_risk_block_reason(message)
    if block_reason:
        return {"status": "blocked", "verification_status": "BLOCKED_RISKY_ACTION", "write_type": "blocked", "summary": block_reason, "evidence": []}
    if REMINDER_DELETE_RE.search(message or ""):
        return {"status": "blocked", "verification_status": "BLOCKED_RISKY_ACTION", "write_type": "reminder_delete", "summary": "Reminder deletion is blocked in this phase.", "evidence": []}
    if REMINDER_UPDATE_RE.search(message or ""):
        return update_verified_reminder(message)
    if REMINDER_CREATE_RE.search(message or ""):
        return create_verified_reminder(message)
    if TASK_NOTE_RE.search(message or ""):
        approved = (message or "").strip().upper().startswith(LOW_RISK_APPROVAL_PHRASE)
        if not approved:
            return {
                "status": "needs_approval",
                "verification_status": "NEEDS_APPROVAL",
                "write_type": "task_note",
                "summary": "Can create a non-sensitive task note under /root/.hermes/agent_tasks/reports only after exact approval.",
                "evidence": [{"type": "approval_required", "phrase": LOW_RISK_APPROVAL_PHRASE}],
            }
        note = task_note_body(message, task_id, cls)
        note_path = write_report(f"{task_id}_note", note)
        ok = note_path.exists() and note_path.stat().st_size > 0 and str(note_path).startswith(str(REPORT_DIR))
        return {
            "status": "completed" if ok else "failed",
            "verification_status": "VERIFIED" if ok else "NOT VERIFIED",
            "write_type": "task_note",
            "summary": "Non-sensitive task note written to approved Hermes report storage." if ok else "Task note write could not be verified.",
            "files_written": [str(note_path)] if ok else [],
            "evidence": [{"type": "file_exists", "path": str(note_path), "size": note_path.stat().st_size if note_path.exists() else 0}],
        }
    return {"status": "blocked", "verification_status": "NOT VERIFIED", "write_type": "unknown", "summary": "Request is not an approved low-risk write action.", "evidence": []}


def low_risk_write_report(task_id: str, message: str, cls: Dict[str, Any], action: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "LOW_RISK_WRITE_REPORT": True,
        "TASK_REPORT": True,
        "task_id": task_id,
        "assigned_agent": cls["recommended_agent"],
        "agent": cls["recommended_agent"],
        "route": cls.get("route"),
        "provider": cls.get("provider"),
        "model": cls.get("model"),
        "status": action.get("status"),
        "write_type": action.get("write_type"),
        "approved_by_user": bool((message or "").strip().upper().startswith(LOW_RISK_APPROVAL_PHRASE)),
        "approval_phrase_seen": LOW_RISK_APPROVAL_PHRASE if (message or "").strip().upper().startswith(LOW_RISK_APPROVAL_PHRASE) else "",
        "files_written": action.get("files_written", []),
        "reminder_job_id": action.get("reminder_job_id"),
        "next_run_at": action.get("next_run_at"),
        "verification_status": action.get("verification_status", "NOT VERIFIED"),
        "evidence": action.get("evidence", []),
        "summary": action.get("summary"),
        "actions_not_taken": ["No Hermes source/config edits.", "No service restarts.", "No package installs.", "No database writes.", "No provider/model routing changes.", "No Gmail/YouTube actions.", "No arbitrary shell execution.", "No reminder deletion."],
        "risks_or_warnings": ["Low-risk write allow-list enforced.", "Task notes require exact approval phrase.", "Reminder writes must pass the existing reminder validation and storage verification flow."],
        "verification_recommendation": "Return VERIFIED only when evidence is present.",
        "final_answer_suggestion": "Report concise evidence; ask for missing information or approval when required.",
    }


def execute_low_risk_write(message: str) -> Dict[str, Any]:
    ensure_dirs()
    cls = classify(message)
    task_id = task_id_for("low-risk-write:" + message)
    action = low_risk_write_action(message, cls, task_id)
    report = low_risk_write_report(task_id, message, cls, action)
    path = write_report(task_id, report)
    record = {
        "task_id": task_id,
        "timestamp": now_iso(),
        "user_intent_summary": mask((message or "")[:240]),
        "assigned_agent": cls["recommended_agent"],
        "route": cls.get("route"),
        "provider": cls.get("provider"),
        "model": cls.get("model"),
        "status": report["status"],
        "risk_level": "low" if report["verification_status"] in {"VERIFIED", "NEEDS_APPROVAL", "NOT VERIFIED"} else "blocked",
        "low_risk_write": True,
        "write_type": report.get("write_type"),
        "evidence_required": True,
        "report_path": str(path),
        "verification_status": report["verification_status"],
    }
    write_ledger(record)
    return {"task_id": task_id, "classification": cls, "report_path": str(path), "report": report}


def format_low_risk_write_response(result: Dict[str, Any]) -> str:
    report = result["report"]
    lines = [
        "LOW_RISK_WRITE_REPORT=CREATED",
        "task_id=" + str(result.get("task_id")),
        "assigned_agent=" + str(report.get("assigned_agent")),
        "route=" + str(report.get("route")),
        "provider=" + str(report.get("provider")),
        "model=" + str(report.get("model")),
        "status=" + str(report.get("status")),
        "write_type=" + str(report.get("write_type")),
        "approved_by_user=" + str(report.get("approved_by_user")).lower(),
        "verification_status=" + str(report.get("verification_status")),
        "summary=" + str(report.get("summary")),
    ]
    if report.get("files_written"):
        lines.append("files_written=" + "; ".join(map(str, report.get("files_written") or [])))
    if report.get("reminder_job_id"):
        lines.append("reminder_job_id=" + str(report.get("reminder_job_id")))
    if report.get("next_run_at"):
        lines.append("next_run_at=" + str(report.get("next_run_at")))
    if report.get("evidence"):
        lines.append("evidence=" + mask(json.dumps(report.get("evidence"), ensure_ascii=False))[:1200])
    lines.append("actions_not_taken=" + "; ".join(map(str, report.get("actions_not_taken") or [])))
    return "\n".join(lines)

def status(limit: int = 10) -> List[Dict[str, Any]]:
    if not LEDGER.exists():
        return []
    rows = []
    for line in LEDGER.read_text(encoding="utf-8", errors="ignore").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return list(reversed(rows))


def friendly_task_time(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt = dt.astimezone(CHINA_TZ)
        hour = dt.strftime("%I").lstrip("0") or "12"
        return f"{dt.strftime('%B')} {dt.day}, {dt.year}, {hour}:{dt.strftime('%M %p')} China time"
    except Exception:
        return mask(raw)


def clean_task_summary(row: Dict[str, Any]) -> str:
    text = str(row.get("user_intent_summary") or row.get("summary") or "Delegated task").strip()
    text = re.sub(r"^\s*YES,\s*EXECUTE\s+LOW-RISK\s+WRITE\s*:\s*", "", text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\b[0-9a-f]{12}\b", "<job_id>", text, flags=re.I)
    if not text:
        return "Delegated task"
    return mask(text[:120])


def task_type(row: Dict[str, Any]) -> str:
    if row.get("write_type") == "task_note":
        return "low-risk task note"
    if row.get("write_type") == "reminder_create":
        return "low-risk reminder create"
    if row.get("write_type") == "reminder_update":
        return "low-risk reminder update"
    if row.get("read_only"):
        return "read-only check"
    if row.get("dry_run"):
        return "dry-run delegation plan"
    if row.get("low_risk_write"):
        return "low-risk write"
    return str(row.get("route") or "delegated task")


def status_reason(row: Dict[str, Any]) -> str:
    verification = str(row.get("verification_status") or row.get("status") or "").strip()
    if verification == "BLOCKED_RISKY_ACTION":
        return "Reason: risky action blocked"
    if verification == "NEEDS_APPROVAL":
        return "Reason: approval required before writing"
    if verification == "NOT_EXECUTED_DRY_RUN":
        return "Reason: dry-run only, no execution"
    if verification in {"FAILED", "NOT VERIFIED"}:
        return "Reason: evidence missing or command failed"
    return ""


def format_status_friendly(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "No delegated tasks found in storage."
    lines = ["Recent delegated tasks:"]
    for idx, row in enumerate(rows, 1):
        verification = str(row.get("verification_status") or row.get("status") or "NOT VERIFIED")
        lines.append("")
        lines.append(f"{idx}. {clean_task_summary(row)}")
        if row.get("assigned_agent"):
            lines.append(f"   Agent: {mask(row.get('assigned_agent'))}")
        lines.append(f"   Status: {mask(verification)}")
        lines.append(f"   Type: {mask(task_type(row))}")
        t = friendly_task_time(row.get("timestamp"))
        if t:
            lines.append(f"   Time: {t}")
        reason = status_reason(row)
        if reason:
            lines.append(f"   {reason}")
    return "\n".join(lines)


def format_status_raw(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "NO_DELEGATED_TASKS_FOUND"
    return "\n".join(json.dumps({k: mask(v) for k, v in row.items()}, ensure_ascii=False, sort_keys=True) for row in rows)


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
    p_status.add_argument("--format", choices=["friendly", "raw"], default="friendly")
    p_read = sub.add_parser("execute-readonly", help="Execute a permission-gated read-only delegated task.")
    p_read.add_argument("message")
    p_read.add_argument("--format", choices=["friendly", "raw"], default="friendly")
    p_low = sub.add_parser("execute-low-risk-write", help="Execute a permission-gated low-risk write task.")
    p_low.add_argument("message")
    p_low.add_argument("--format", choices=["friendly", "raw"], default="friendly")
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
                print("report_path=" + result.get("report_path", ""))
                print("verification_status=NOT_EXECUTED_DRY_RUN")
                print("required_user_inputs=" + "; ".join(map(str, result.get("report", {}).get("required_user_inputs", []))))
                print("proposed_actions=" + "; ".join(map(str, result.get("report", {}).get("proposed_steps", []))))
                print("prohibited_actions=" + "; ".join(map(str, result.get("report", {}).get("actions_not_taken", []))))
            else:
                print("report_path=" + result["report_path"])
                print("verification_status=" + ("VERIFIED" if result["verification"]["verified"] else "NOT VERIFIED"))
        return 0
    if args.cmd == "execute-readonly":
        result = execute_readonly(args.message)
        if args.format == "raw":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_readonly_response(result))
        return 0
    if args.cmd == "execute-low-risk-write":
        result = execute_low_risk_write(args.message)
        if args.format == "raw":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_low_risk_write_response(result))
        return 0
    if args.cmd == "status":
        rows = status(args.limit)
        if args.format == "raw":
            print(format_status_raw(rows))
        else:
            print(format_status_friendly(rows))
        return 0
    parser.print_help()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
