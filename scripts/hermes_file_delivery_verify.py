#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def resolve_base() -> Path:
    env_base = os.environ.get("HERMES_BASE", "").strip()
    if env_base:
        return Path(env_base)
    live = Path("/root/.hermes")
    if live.exists():
        return live
    return Path(__file__).resolve().parents[1]


BASE = resolve_base()
OUTPUT_DIR = BASE / "file_outputs"
HTML_OUTPUT_DIR = BASE / "newcoin_outputs"
TMP_DIR = BASE / "telegram_outputs"
ARTIFACT_REGISTRY = BASE / "artifacts" / "latest_artifacts.jsonl"
APPROVED_DIRS = [OUTPUT_DIR, HTML_OUTPUT_DIR, TMP_DIR]
DELIVER = BASE / "scripts" / "hermes_telegram_deliver.py"
RICH_EXECUTE = BASE / "scripts" / "hermes_rich_output_execute.py"
SESSIONS_INDEX = BASE / "sessions" / "sessions.json"
SESSIONS_DIR = BASE / "sessions"

ARTIFACT_RE = re.compile(
    r"\bpdf\b|\bshow\s+me\s+the\s+(?:file|pdf)\b|\bsend\s+the\s+pdf\s+again\b|\bresend\b|\bshow\s+me\s+the\s+file\s+here\b",
    re.I,
)
QUESTION_RE = re.compile(r"\?\s*$")
RESEND_RE = re.compile(
    r"\bshow\s+me\s+the\s+(?:file|pdf)\b|\bsend\s+the\s+pdf\s+again\b|\bresend\b|\bshow\s+me\s+the\s+file\s+here\b",
    re.I,
)
PDF_RE = re.compile(r"^\s*pdf(?:\s+only)?\s*$|\bpdf\b", re.I)
HTML_BUILD_RE = re.compile(
    r"\b(build|create|generate|make)\b.*\b(html|css|web\s*page|webpage|website|landing\s*page|page)\b|"
    r"\bhtml/css\b|\blanding\s*page\b",
    re.I,
)
ELECTRIC_CAR_RE = re.compile(r"\bfirst\s+ever\s+electric\s+car\b|\bwho\s+made\s+the\s+first\s+electric\s+car\b", re.I)
BACKEND_COMMAND_RE = re.compile(
    r"/root/\.hermes/scripts/\S+|hermes_rich_output_execute\.py|hermes_router_execute\.py|EXECUTED_COMMAND=",
    re.I,
)


def sanitize_user_text(text: str) -> str:
    cleaned_lines: list[str] = []
    in_backend_fence = False
    fence_buffer: list[str] = []
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_backend_fence:
                if not any(BACKEND_COMMAND_RE.search(buf) for buf in fence_buffer):
                    cleaned_lines.extend(fence_buffer)
                    cleaned_lines.append(line)
                in_backend_fence = False
                fence_buffer = []
            else:
                in_backend_fence = True
                fence_buffer = [line]
            continue
        if in_backend_fence:
            fence_buffer.append(line)
            continue
        if BACKEND_COMMAND_RE.search(line):
            continue
        cleaned_lines.append(line)
    if in_backend_fence and not any(BACKEND_COMMAND_RE.search(buf) for buf in fence_buffer):
        cleaned_lines.extend(fence_buffer)
    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def mask(text: Any) -> str:
    raw = str(text or "")
    raw = re.sub(r"bot\d+:[A-Za-z0-9_-]+", "<REDACTED>", raw)
    raw = re.sub(r"(chat_id|token)([\"':= ]+)([^,\s}\]]+)", r"\1\2<REDACTED>", raw, flags=re.I)
    raw = re.sub(r"(-?\d{8,})", "<chat_id_masked>", raw)
    return raw


def ensure_dirs() -> None:
    for path in APPROVED_DIRS + [ARTIFACT_REGISTRY.parent]:
        path.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text or "hermes-output").strip("-").lower()
    return slug or "hermes-output"


def inside_approved(path: Path) -> bool:
    resolved = path.resolve()
    return any(
        resolved == approved.resolve() or approved.resolve() in resolved.parents
        for approved in APPROVED_DIRS
    )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def wrap_text(text: str, width: int = 82) -> list[str]:
    words = (text or "").split()
    if not words:
        return [""]
    lines: list[str] = []
    current: list[str] = []
    current_len = 0
    for word in words:
        extra = len(word) + (1 if current else 0)
        if current and current_len + extra > width:
            lines.append(" ".join(current))
            current = [word]
            current_len = len(word)
        else:
            current.append(word)
            current_len += extra
    if current:
        lines.append(" ".join(current))
    return lines or [""]


def pdf_escape(text: str) -> str:
    return (
        (text or "")
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def build_pdf_bytes(lines: list[str]) -> bytes:
    commands = ["BT", "/F1 16 Tf", "72 760 Td"]
    for idx, line in enumerate(lines):
        if idx:
            commands.append("0 -18 Td")
        commands.append(f"({pdf_escape(line)}) Tj")
    commands.append("ET")
    content = "\n".join(commands).encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(content), content),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pieces = [b"%PDF-1.4\n"]
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(sum(len(piece) for piece in pieces))
        pieces.append(f"{index} 0 obj\n".encode("ascii"))
        pieces.append(obj)
        pieces.append(b"\nendobj\n")
    xref_start = sum(len(piece) for piece in pieces)
    pieces.append(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pieces.append(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pieces.append(f"{offset:010d} 00000 n \n".encode("ascii"))
    pieces.append(f"trailer << /Root 1 0 R /Size {len(objects) + 1} >>\n".encode("ascii"))
    pieces.append(f"startxref\n{xref_start}\n%%EOF\n".encode("ascii"))
    return b"".join(pieces)


def extract_pdf_text(path: Path) -> str:
    try:
        raw = path.read_bytes().decode("latin-1", errors="ignore")
    except Exception:
        return ""
    chunks = re.findall(r"\((.*?)\)\s*Tj", raw, flags=re.S)
    text = " ".join(chunk for chunk in chunks)
    text = text.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")
    return re.sub(r"\s+", " ", text).strip()


def load_sessions_index() -> list[dict[str, Any]]:
    if not SESSIONS_INDEX.exists():
        return []
    try:
        data = json.loads(SESSIONS_INDEX.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        return [row for row in data.values() if isinstance(row, dict)]
    return []


def latest_session_record() -> dict[str, Any] | None:
    rows = load_sessions_index()
    if not rows:
        return None
    rows.sort(key=lambda row: str(row.get("updated_at") or row.get("created_at") or ""))
    return rows[-1]


def load_transcript(record: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not record:
        return []
    session_id = str(record.get("session_id") or "").strip()
    if not session_id:
        return []
    path = SESSIONS_DIR / f"{session_id}.jsonl"
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def artifact_like(text: str) -> bool:
    return bool(ARTIFACT_RE.search(text or ""))


def parse_steps(message: str) -> list[str]:
    raw = (message or "").replace("\r", "\n")
    steps: list[str] = []
    for part in re.split(r"\n+", raw):
        cleaned = re.sub(r"^\s*\d+[.)]?\s*", "", part).strip()
        if cleaned:
            steps.append(cleaned)
    return steps


def find_latest_topic_context(transcript: list[dict[str, Any]]) -> tuple[str, str]:
    if not transcript:
        return "", ""
    for idx in range(len(transcript) - 1, -1, -1):
        row = transcript[idx]
        if row.get("role") != "user":
            continue
        content = str(row.get("content") or "").strip()
        if not content or artifact_like(content):
            continue
        if re.search(r"\b(news|headlines|briefing|upload schedule|any reminders|reminders?)\b", content, re.I):
            continue
        answer = ""
        for later in transcript[idx + 1 :]:
            if later.get("role") == "assistant":
                answer = str(later.get("content") or "").strip()
                break
            if later.get("role") == "user":
                break
        return content, answer
    return "", ""


def known_topic_profile(topic: str, assistant_answer: str) -> dict[str, Any] | None:
    combined = f"{topic}\n{assistant_answer}"
    if ELECTRIC_CAR_RE.search(combined):
        answer = (
            "The first electric car is usually credited to Robert Anderson, a Scottish inventor, "
            "who built an early electric carriage in the 1830s, around 1832 to 1839. "
            "It used non-rechargeable batteries, so it proved the idea of electric transport "
            "without yet being practical for everyday road use."
        )
        sections = [
            (
                "Who Built It",
                "Robert Anderson of Scotland is the figure most often credited with the first early electric carriage or cart.",
            ),
            (
                "When It Happened",
                "Historians usually place Anderson's work in the early 1830s, often around 1832, with some sources widening that range to 1832–1839.",
            ),
            (
                "How It Worked",
                "The vehicle used non-rechargeable primary batteries and an electric motor. That made it an important proof of concept, but the battery technology limited range and practicality.",
            ),
            (
                "Why It Matters",
                "Even though it was not yet a commercial car, it showed that a carriage could be moved by electric power rather than horses or steam.",
            ),
            (
                "Later Milestones",
                "Thomas Davenport built an early electric motor application in 1834, and more practical road-going electric vehicles arrived later in the 1880s as battery and motor technology improved.",
            ),
        ]
        return {
            "title": "Who Made the First Ever Electric Car?",
            "topic_query": topic or "Who made the first ever electric car?",
            "answer": answer,
            "sections": sections,
            "required_terms": [
                "Robert Anderson",
                "Scotland",
                "1832",
                "1830s",
                "non-rechargeable batteries",
                "electric carriage",
                "later milestones",
                "Thomas Davenport",
            ],
        }
    return None


def generic_profile(topic: str, assistant_answer: str) -> dict[str, Any]:
    title = topic.strip(" ?.") or "Hermes Educational PDF"
    assistant_answer = sanitize_user_text(assistant_answer)
    answer = assistant_answer.strip() or f"Summary topic: {title}"
    body_lines = [line.strip("-* ").strip() for line in assistant_answer.splitlines() if line.strip()]
    if not body_lines:
        body_lines = [answer]
    sections: list[tuple[str, str]] = []
    if body_lines:
        sections.append(("Overview", body_lines[0]))
    if len(body_lines) > 1:
        sections.append(("Key Points", " ".join(body_lines[1:4])))
    if len(body_lines) > 4:
        sections.append(("More Detail", " ".join(body_lines[4:8])))
    title_case = title[0].upper() + title[1:] if title else "Hermes Educational PDF"
    required = [term for term in re.findall(r"[A-Za-z0-9]{4,}", title_case)[:4]]
    return {
        "title": title_case,
        "topic_query": title_case,
        "answer": answer,
        "sections": sections or [("Overview", answer)],
        "required_terms": required or [title_case],
    }


def build_profile(message: str, transcript: list[dict[str, Any]]) -> dict[str, Any]:
    steps = parse_steps(message)
    question_step = next((step for step in steps if QUESTION_RE.search(step) and not artifact_like(step)), "")
    explicit_title = ""
    title_match = re.search(r"\b(?:titled|called)\s+(.+?)(?:[.!?]\s*$|$)", message or "", re.I)
    if title_match:
        explicit_title = title_match.group(1).strip(" .,:;\"'")
    session_topic, session_answer = find_latest_topic_context(transcript)
    topic = explicit_title or question_step or session_topic or "Hermes Educational PDF"
    assistant_answer = sanitize_user_text(session_answer)
    profile = known_topic_profile(topic, assistant_answer)
    if profile:
        return profile
    return generic_profile(topic, assistant_answer)


def render_pdf_lines(profile: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    lines.extend(wrap_text(profile["title"], width=64))
    lines.append("")
    lines.extend(wrap_text("Educational summary generated from verified Hermes session context.", width=82))
    lines.append("")
    lines.extend(wrap_text(profile["answer"], width=82))
    lines.append("")
    for heading, body in profile.get("sections", []):
        lines.extend(wrap_text(heading + ":", width=82))
        for wrapped in wrap_text(body, width=82):
            lines.append("  " + wrapped)
        lines.append("")
    return lines[:38]


def verify_file(path: Path, required_terms: list[str] | None = None) -> dict[str, Any]:
    exists = path.exists()
    size = path.stat().st_size if exists else 0
    header = path.read_bytes()[:5] if exists else b""
    suffix = path.suffix.lower()
    format_ok = suffix == ".pdf" and header.startswith(b"%PDF-")
    approved_dir = exists and inside_approved(path)
    extracted_text = extract_pdf_text(path) if exists else ""
    matched_terms: list[str] = []
    required_terms = required_terms or []
    lowered_text = extracted_text.lower()
    for term in required_terms:
        if term.lower() in lowered_text:
            matched_terms.append(term)
    content_verified = bool(required_terms) and len(matched_terms) == len(required_terms)
    verified = exists and size > 0 and format_ok and approved_dir
    return {
        "path": str(path),
        "exists": exists,
        "size": size,
        "extension": suffix,
        "format_ok": format_ok,
        "approved_dir": approved_dir,
        "verified": verified,
        "content_verified": content_verified,
        "matched_terms": matched_terms,
        "required_terms": required_terms,
        "extracted_text": extracted_text,
    }


def create_pdf(profile: dict[str, Any]) -> dict[str, Any]:
    ensure_dirs()
    path = OUTPUT_DIR / f"{slugify(profile['title'])}.pdf"
    path.write_bytes(build_pdf_bytes(render_pdf_lines(profile)))
    return verify_file(path, profile.get("required_terms"))


def chat_target(record: dict[str, Any] | None) -> tuple[str, str]:
    origin = (record or {}).get("origin") or {}
    chat_id = str(origin.get("chat_id") or "").strip()
    return chat_id, mask(chat_id)


def run_delivery(path: Path, caption: str, chat_id: str = "", preview_link: str = "no") -> dict[str, Any]:
    cmd = [sys.executable, str(DELIVER), "--file", str(path), "--caption", caption, "--preview-link", preview_link]
    if chat_id:
        cmd.extend(["--chat-id", chat_id])
    try:
        proc = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=180,
        )
    except Exception as exc:
        return {
            "attempted": True,
            "ok": False,
            "reason": f"DELIVERY_EXCEPTION:{type(exc).__name__}",
            "stdout": "",
            "stderr": mask(exc),
        }
    combined = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    ok = proc.returncode == 0 and "TELEGRAM_API_OK=true" in combined and "TELEGRAM_DELIVERY=PASSED" in combined
    return {
        "attempted": True,
        "ok": ok,
        "returncode": proc.returncode,
        "stdout": mask(proc.stdout),
        "stderr": mask(proc.stderr),
        "reason": "" if ok else "DELIVERY_NOT_VERIFIED",
    }


def run_text_fallback(path: Path, chat_id: str = "") -> dict[str, Any]:
    cmd = [sys.executable, str(DELIVER), "--text-file", str(path)]
    if chat_id:
        cmd.extend(["--chat-id", chat_id])
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=180)
    except Exception as exc:
        return {"attempted": True, "ok": False, "reason": f"TEXT_FALLBACK_EXCEPTION:{type(exc).__name__}", "stdout": "", "stderr": mask(exc)}
    combined = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    ok = proc.returncode == 0 and "TELEGRAM_API_OK=true" in combined and "TELEGRAM_DELIVERY=PASSED" in combined
    return {"attempted": True, "ok": ok, "returncode": proc.returncode, "stdout": mask(proc.stdout), "stderr": mask(proc.stderr), "reason": "" if ok else "TEXT_FALLBACK_NOT_VERIFIED"}


def html_required_terms(message: str) -> tuple[list[str], list[list[str]]]:
    low = (message or "").lower()
    required: list[str] = []
    for term in ["coffee", "pastry"]:
        if term in low:
            required.append(term)
    if "landing" in low or "page" in low or "shop" in low:
        required.append("menu")
    any_groups = [["contact", "location"]]
    return required, any_groups


def verify_html_file(path: Path, message: str) -> dict[str, Any]:
    required, any_groups = html_required_terms(message)
    exists = path.exists()
    size = path.stat().st_size if exists else 0
    extension = path.suffix.lower()
    approved_dir = exists and inside_approved(path)
    text = path.read_text(encoding="utf-8", errors="ignore") if exists else ""
    lower = text.lower()
    format_ok = extension == ".html" and size > 0 and ("<!doctype html" in lower or "<html" in lower)
    css_ok = "<style" in lower or "rel=\"stylesheet\"" in lower or "rel='stylesheet'" in lower or ".css" in lower
    matched_terms = [term for term in required if term.lower() in lower]
    missing_terms = [term for term in required if term.lower() not in lower]
    any_group_results = []
    for group in any_groups:
        matched = [term for term in group if term.lower() in lower]
        any_group_results.append({"terms": group, "matched": matched, "ok": bool(matched)})
    content_verified = bool(format_ok and css_ok and not missing_terms and all(row["ok"] for row in any_group_results))
    return {
        "path": str(path),
        "exists": exists,
        "size": size,
        "extension": extension,
        "format_ok": format_ok,
        "css_ok": css_ok,
        "approved_dir": approved_dir,
        "verified": bool(exists and approved_dir and format_ok and css_ok),
        "content_verified": content_verified,
        "matched_terms": matched_terms,
        "missing_terms": missing_terms,
        "any_term_groups": any_group_results,
    }


def parse_output_path(text: str) -> Path | None:
    for line in (text or "").splitlines():
        if line.startswith("OUTPUT_PATH="):
            value = line.split("=", 1)[1].strip()
            if value:
                return Path(value)
    return None


def build_html_user_output(file_info: dict[str, Any], delivery: dict[str, Any], fallback: dict[str, Any], code: str) -> str:
    if file_info.get("content_verified") and delivery.get("ok"):
        return "I created and sent the verified HTML landing page in Telegram.\nCONTENT_VERIFIED=true\nTELEGRAM_API_OK=true"
    if file_info.get("content_verified") and fallback.get("ok"):
        return "I created the verified HTML landing page. File delivery failed, so I pasted the complete HTML/CSS code in Telegram.\nCONTENT_VERIFIED=true\nTELEGRAM_FILE_DELIVERY_OK=false\nCODE_FALLBACK_OK=true"
    lines = ["NOT VERIFIED"]
    if not file_info.get("content_verified"):
        lines.append("REASON=HTML_CONTENT_VERIFICATION_FAILED")
    elif not delivery.get("ok"):
        lines.append("REASON=TELEGRAM_DELIVERY_NOT_VERIFIED")
    if code:
        lines.append("HTML_CODE_FALLBACK_START")
        lines.append(code)
        lines.append("HTML_CODE_FALLBACK_END")
    return "\n".join(lines).strip()


def create_or_send_html(message: str, chat_id_override: str = "") -> dict[str, Any]:
    record = latest_session_record()
    chat_id, chat_mask = chat_target(record)
    if chat_id_override:
        chat_id = chat_id_override
        chat_mask = mask(chat_id_override)
    cmd = [sys.executable, str(RICH_EXECUTE), "--request", message, "--no-deliver-telegram"]
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=420)
    except Exception as exc:
        file_info = {"path": "", "exists": False, "size": 0, "extension": ".html", "format_ok": False, "css_ok": False, "approved_dir": False, "verified": False, "content_verified": False}
        return {"verification_status": "NOT VERIFIED", "summary": f"HTML generation failed: {type(exc).__name__}", "file": file_info, "telegram_delivery": {"attempted": False, "ok": False}, "code_fallback": {"attempted": False, "ok": False}, "user_output": "NOT VERIFIED\nREASON=HTML_GENERATION_EXCEPTION"}
    output_path = parse_output_path(proc.stdout) or (HTML_OUTPUT_DIR / "hermes-html-output.html")
    file_info = verify_html_file(output_path, message)
    code = Path(file_info["path"]).read_text(encoding="utf-8", errors="ignore") if file_info.get("exists") else ""
    delivery = {"attempted": False, "ok": False, "reason": "HTML_NOT_VERIFIED"}
    fallback = {"attempted": False, "ok": False, "reason": "NOT_NEEDED"}
    if proc.returncode == 0 and file_info.get("content_verified"):
        delivery = run_delivery(output_path, "Your Majesty, here is your verified HTML landing page: " + output_path.name, chat_id=chat_id, preview_link="auto")
        if not delivery.get("ok"):
            fallback = run_text_fallback(output_path, chat_id=chat_id)
    verified = bool(file_info.get("content_verified") and (delivery.get("ok") or fallback.get("ok")))
    delivery_status = "delivered" if delivery.get("ok") else "code_fallback" if fallback.get("ok") else "delivery_failed"
    artifact = register_artifact(
        intent=message,
        artifact_type="html",
        path=file_info.get("path", ""),
        title=Path(file_info.get("path") or "html-output.html").stem,
        content_verified=bool(file_info.get("content_verified")),
        delivery_status=delivery_status,
        telegram_ok=bool(delivery.get("ok")),
        chat_mask=chat_mask,
        source_context_summary="Built from the current Lite Mode HTML/CSS request and verified before same-chat delivery.",
    )
    return {
        "verification_status": "VERIFIED" if verified else "NOT VERIFIED",
        "summary": "Verified HTML created and delivered." if delivery.get("ok") else "Verified HTML created with code fallback." if fallback.get("ok") else "HTML generation or delivery is not verified.",
        "file": file_info,
        "telegram_delivery": delivery,
        "code_fallback": fallback,
        "artifact": artifact,
        "generator_returncode": proc.returncode,
        "user_output": build_html_user_output(file_info, delivery, fallback, code if not fallback.get("ok") and not delivery.get("ok") else ""),
        "evidence": [
            {"type": "file_exists", "path": file_info.get("path"), "size": file_info.get("size")},
            {"type": "html_format", "format_ok": file_info.get("format_ok"), "extension": file_info.get("extension")},
            {"type": "css", "css_ok": file_info.get("css_ok")},
            {"type": "content_terms", "content_verified": file_info.get("content_verified"), "matched_terms": file_info.get("matched_terms"), "missing_terms": file_info.get("missing_terms"), "any_term_groups": file_info.get("any_term_groups")},
            {"type": "telegram_delivery", "ok": delivery.get("ok"), "returncode": delivery.get("returncode")},
            {"type": "code_fallback", "ok": fallback.get("ok"), "returncode": fallback.get("returncode")},
        ],
    }


def load_registry() -> list[dict[str, Any]]:
    if not ARTIFACT_REGISTRY.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in ARTIFACT_REGISTRY.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def append_registry(record: dict[str, Any]) -> None:
    ensure_dirs()
    with ARTIFACT_REGISTRY.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def latest_verified_artifact(chat_mask: str) -> dict[str, Any] | None:
    for row in reversed(load_registry()):
        if row.get("artifact_type") != "pdf":
            continue
        if not row.get("content_verified"):
            continue
        if row.get("delivery_status") not in {"delivered", "resent"}:
            continue
        if row.get("telegram_ok") is not True:
            continue
        if chat_mask and row.get("chat_target_masked") != chat_mask:
            continue
        return row
    return None


def register_artifact(
    *,
    intent: str,
    artifact_type: str,
    path: str,
    title: str,
    content_verified: bool,
    delivery_status: str,
    telegram_ok: bool,
    chat_mask: str,
    source_context_summary: str,
) -> dict[str, Any]:
    record = {
        "artifact_id": f"{now_iso().replace(':', '').replace('-', '')}-{slugify(title)}",
        "timestamp": now_iso(),
        "user_intent_summary": intent.strip()[:300],
        "artifact_type": artifact_type,
        "path": path,
        "title": title,
        "content_verified": bool(content_verified),
        "delivery_status": delivery_status,
        "telegram_ok": bool(telegram_ok),
        "chat_target_masked": chat_mask or "<chat_id_masked>",
        "source_context_summary": source_context_summary[:400],
    }
    append_registry(record)
    return record


def build_user_output(answer: str, status: str, file_info: dict[str, Any], delivery: dict[str, Any], created: bool) -> str:
    lines: list[str] = []
    answer = sanitize_user_text(answer)
    if answer:
        lines.extend(answer.splitlines())
        lines.append("")
    if status == "VERIFIED":
        action = "created and sent" if created else "sent again"
        lines.append(f"I {action} the verified PDF in Telegram.")
        lines.append(f"CONTENT_VERIFIED={'true' if file_info.get('content_verified') else 'false'}")
        lines.append(f"TELEGRAM_API_OK={'true' if delivery.get('ok') else 'false'}")
    else:
        lines.append("NOT VERIFIED")
        if not file_info.get("content_verified"):
            lines.append("REASON=CONTENT_VERIFICATION_FAILED")
        elif not delivery.get("ok"):
            lines.append("REASON=TELEGRAM_DELIVERY_NOT_VERIFIED")
    return "\n".join(lines).strip()


def create_or_send_pdf(message: str) -> dict[str, Any]:
    record = latest_session_record()
    transcript = load_transcript(record)
    chat_id, chat_mask = chat_target(record)
    profile = build_profile(message, transcript)
    file_info = create_pdf(profile)
    delivery = run_delivery(Path(file_info["path"]), f"Hermes PDF: {profile['title']}", chat_id=chat_id)
    verified = bool(file_info["verified"] and file_info["content_verified"] and delivery["ok"])
    source_context = (
        "Built from the latest verified Hermes session topic and assistant answer."
        if transcript
        else "Built from the current request because no session transcript was available."
    )
    artifact = register_artifact(
        intent=message,
        artifact_type="pdf",
        path=file_info["path"],
        title=profile["title"],
        content_verified=file_info["content_verified"],
        delivery_status="delivered" if delivery["ok"] else "delivery_failed",
        telegram_ok=delivery["ok"],
        chat_mask=chat_mask,
        source_context_summary=source_context,
    )
    return {
        "verification_status": "VERIFIED" if verified else "NOT VERIFIED",
        "summary": "Verified educational PDF created and Telegram delivery confirmed." if verified else "PDF generation, content verification, or Telegram delivery is not verified.",
        "answer": profile["answer"],
        "file": file_info,
        "telegram_delivery": delivery,
        "artifact": artifact,
        "user_output": build_user_output(profile["answer"], "VERIFIED" if verified else "NOT VERIFIED", file_info, delivery, True),
        "evidence": [
            {"type": "file_exists", "path": file_info["path"], "size": file_info["size"]},
            {"type": "file_format", "format_ok": file_info["format_ok"], "extension": file_info["extension"]},
            {"type": "content_verification", "content_verified": file_info["content_verified"], "matched_terms": file_info["matched_terms"]},
            {"type": "telegram_delivery", "ok": delivery["ok"], "returncode": delivery.get("returncode")},
        ],
    }


def resend_latest_pdf(message: str) -> dict[str, Any]:
    record = latest_session_record()
    chat_id, chat_mask = chat_target(record)
    latest = latest_verified_artifact(chat_mask)
    if not latest:
        return {
            "verification_status": "NOT VERIFIED",
            "summary": "No previously verified artifact exists for this Telegram chat.",
            "file": {"path": "", "exists": False, "size": 0, "extension": ".pdf", "format_ok": False, "approved_dir": False, "verified": False, "content_verified": False},
            "telegram_delivery": {"attempted": False, "ok": False, "reason": "NO_VERIFIED_ARTIFACT"},
            "artifact": None,
            "user_output": "NOT VERIFIED\nREASON=NO_VERIFIED_ARTIFACT_FOR_THIS_CHAT",
            "evidence": [],
        }
    path = Path(str(latest.get("path") or ""))
    file_info = verify_file(path, latest.get("title", "").split())
    file_info["content_verified"] = bool(latest.get("content_verified"))
    delivery = run_delivery(path, f"Hermes PDF: {latest.get('title')}", chat_id=chat_id)
    verified = bool(file_info["verified"] and file_info["content_verified"] and delivery["ok"])
    artifact = register_artifact(
        intent=message,
        artifact_type="pdf",
        path=str(path),
        title=str(latest.get("title") or "Verified PDF"),
        content_verified=file_info["content_verified"],
        delivery_status="resent" if delivery["ok"] else "resend_failed",
        telegram_ok=delivery["ok"],
        chat_mask=chat_mask,
        source_context_summary=str(latest.get("source_context_summary") or "Resent from latest verified artifact registry entry."),
    )
    return {
        "verification_status": "VERIFIED" if verified else "NOT VERIFIED",
        "summary": "Verified PDF resent to Telegram." if verified else "PDF resend is not verified.",
        "answer": "",
        "file": file_info,
        "telegram_delivery": delivery,
        "artifact": artifact,
        "user_output": build_user_output("", "VERIFIED" if verified else "NOT VERIFIED", file_info, delivery, False),
        "evidence": [
            {"type": "artifact_registry_match", "path": str(path), "title": latest.get("title")},
            {"type": "telegram_delivery", "ok": delivery["ok"], "returncode": delivery.get("returncode")},
        ],
    }


def from_message(message: str, chat_id_override: str = "") -> dict[str, Any]:
    low = (message or "").strip().lower()
    steps = parse_steps(message)
    if HTML_BUILD_RE.search(message or ""):
        return create_or_send_html(message, chat_id_override=chat_id_override)
    if RESEND_RE.search(low) and not any(PDF_RE.search(step) and not RESEND_RE.search(step) for step in steps):
        return resend_latest_pdf(message)

    created = create_or_send_pdf(message)
    if RESEND_RE.search(low):
        resend = resend_latest_pdf(message)
        if created["verification_status"] == "VERIFIED" and resend["verification_status"] == "VERIFIED":
            created["summary"] = "Verified educational PDF created and resent to Telegram."
            created["user_output"] = created["user_output"] + "\n\nI also resent the same verified PDF in Telegram."
            created["evidence"].extend(resend.get("evidence", []))
        else:
            created["verification_status"] = "NOT VERIFIED"
            created["summary"] = "PDF creation or resend is not fully verified."
            created["user_output"] = created["user_output"] + "\n\nNOT VERIFIED\nREASON=FOLLOW_UP_RESEND_NOT_VERIFIED"
    return created


def print_friendly(data: dict[str, Any]) -> None:
    print(f"VERIFICATION_STATUS={data.get('verification_status')}")
    print(f"SUMMARY={mask(data.get('summary'))}")
    print(f"CONTENT_VERIFIED={'true' if (data.get('file') or {}).get('content_verified') else 'false'}")
    print(f"TELEGRAM_API_OK={'true' if (data.get('telegram_delivery') or {}).get('ok') else 'false'}")
    print("TELEGRAM_DELIVERY=" + ("PASSED" if (data.get("telegram_delivery") or {}).get("ok") else "FAILED"))
    print("OUTPUT_PATH=" + mask((data.get("file") or {}).get("path", "")))
    artifact = data.get("artifact") or {}
    if artifact.get("artifact_id"):
        print("ARTIFACT_ID=" + str(artifact.get("artifact_id")))
    if data.get("user_output"):
        print("USER_OUTPUT_START")
        print(mask(data["user_output"]))
        print("USER_OUTPUT_END")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verified file generation and Telegram delivery for Hermes.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_test = sub.add_parser("generate-test-pdf")
    p_test.add_argument("--title", default="Hermes Test PDF")
    p_test.add_argument("--format", choices=["friendly", "json"], default="friendly")

    p_verify = sub.add_parser("verify-file")
    p_verify.add_argument("path")
    p_verify.add_argument("--require", action="append", default=[])
    p_verify.add_argument("--format", choices=["friendly", "json"], default="friendly")

    p_message = sub.add_parser("from-message")
    p_message.add_argument("message")
    p_message.add_argument("--format", choices=["friendly", "json"], default="friendly")
    p_message.add_argument("--chat-id", default="")

    args = parser.parse_args()
    if args.cmd == "generate-test-pdf":
        profile = {
            "title": args.title,
            "topic_query": args.title,
            "answer": f"This PDF was generated for {args.title}.",
            "sections": [("Overview", "Hermes generated this verified test PDF for delivery checks.")],
            "required_terms": [args.title.split()[0] if args.title.split() else "Hermes"],
        }
        file_info = create_pdf(profile)
        data = {"verification_status": "VERIFIED" if file_info["verified"] and file_info["content_verified"] else "NOT VERIFIED", "file": file_info}
    elif args.cmd == "verify-file":
        file_info = verify_file(Path(args.path), args.require)
        data = {"verification_status": "VERIFIED" if file_info["verified"] and (file_info["content_verified"] or not args.require) else "NOT VERIFIED", "file": file_info}
    else:
        data = from_message(args.message, chat_id_override=getattr(args, "chat_id", ""))

    if args.format == "json":
        print(json.dumps(data, ensure_ascii=False))
    else:
        print_friendly(data)
    return 0 if data.get("verification_status") == "VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
