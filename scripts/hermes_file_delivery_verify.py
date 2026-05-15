#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
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
TMP_DIR = BASE / "telegram_outputs"
APPROVED_DIRS = [OUTPUT_DIR, TMP_DIR]
DELIVER = BASE / "scripts" / "hermes_telegram_deliver.py"


def mask(text: Any) -> str:
    raw = str(text or "")
    raw = re.sub(r"bot\d+:[A-Za-z0-9_-]+", "<REDACTED>", raw)
    raw = re.sub(r"(-?\d{8,})", "<chat_id_masked>", raw)
    return raw


def ensure_dirs() -> None:
    for path in APPROVED_DIRS:
        path.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text or "hermes-output").strip("-").lower()
    return slug or "hermes-output"


def inside_approved(path: Path) -> bool:
    resolved = path.resolve()
    return any(resolved == approved.resolve() or approved.resolve() in resolved.parents for approved in APPROVED_DIRS)


def build_pdf_bytes(title: str) -> bytes:
    safe = title.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    content = f"BT /F1 18 Tf 72 720 Td ({safe}) Tj ET"
    lines = [
        "%PDF-1.4",
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
        "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
        "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj",
        f"4 0 obj << /Length {len(content)} >> stream",
        content,
        "endstream endobj",
        "5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
        "xref",
        "0 6",
        "0000000000 65535 f ",
        "trailer << /Root 1 0 R /Size 6 >>",
        "startxref",
        "0",
        "%%EOF",
    ]
    return "\n".join(lines).encode("utf-8")


def verify_file(path: Path) -> dict[str, Any]:
    exists = path.exists()
    size = path.stat().st_size if exists else 0
    header = path.read_bytes()[:5] if exists else b""
    suffix = path.suffix.lower()
    format_ok = suffix == ".pdf" and header.startswith(b"%PDF-")
    approved_dir = exists and inside_approved(path)
    verified = exists and size > 0 and format_ok and approved_dir
    return {
        "path": str(path),
        "exists": exists,
        "size": size,
        "extension": suffix,
        "format_ok": format_ok,
        "approved_dir": approved_dir,
        "verified": verified,
    }


def create_pdf(title: str) -> dict[str, Any]:
    ensure_dirs()
    path = OUTPUT_DIR / f"{slugify(title)}.pdf"
    path.write_bytes(build_pdf_bytes(title))
    return verify_file(path)


def latest_verified_pdf() -> dict[str, Any] | None:
    files = sorted(OUTPUT_DIR.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in files:
        info = verify_file(path)
        if info["verified"]:
            return info
    return None


def run_delivery(path: Path, caption: str) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            [sys.executable, str(DELIVER), "--file", str(path), "--caption", caption, "--preview-link", "no"],
            text=True,
            capture_output=True,
            timeout=180,
        )
    except Exception as exc:
        return {"attempted": True, "ok": False, "reason": f"DELIVERY_EXCEPTION:{type(exc).__name__}", "stdout": "", "stderr": mask(exc)}
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


def title_from_message(message: str) -> str:
    match = re.search(r"\b(?:called|named|titled)\s+(.+?)(?:\s+(?:and\s+)?(?:send|deliver|upload)\b|$)", message or "", re.I)
    if match:
        return match.group(1).strip(" .")
    return "Hermes Verified PDF"


def from_message(message: str) -> dict[str, Any]:
    low = (message or "").strip().lower()
    if re.search(r"\bshow\s+me\s+the\s+file\b.*\btelegram\b|\bshow\s+me\s+the\s+file\s+here\b", low, re.I):
        file_info = latest_verified_pdf()
        if not file_info:
            return {
                "verification_status": "NOT VERIFIED",
                "summary": "No previously verified PDF exists to resend.",
                "file": {"path": "", "exists": False, "size": 0, "extension": ".pdf", "format_ok": False, "approved_dir": False, "verified": False},
                "telegram_delivery": {"attempted": False, "ok": False, "reason": "NO_VERIFIED_FILE"},
                "evidence": [],
            }
        delivery = run_delivery(Path(file_info["path"]), "Your Majesty, here is the verified file again.")
        verified = bool(file_info["verified"] and delivery["ok"])
        return {
            "verification_status": "VERIFIED" if verified else "NOT VERIFIED",
            "summary": "Verified file resent to Telegram." if verified else "File resend is not verified.",
            "file": file_info,
            "telegram_delivery": delivery,
            "evidence": [{"type": "file_exists", "path": file_info["path"], "size": file_info["size"]}, {"type": "telegram_delivery", "ok": delivery["ok"]}],
        }

    file_info = create_pdf(title_from_message(message))
    delivery = run_delivery(Path(file_info["path"]), "Your Majesty, here is your verified PDF.")
    verified = bool(file_info["verified"] and delivery["ok"])
    return {
        "verification_status": "VERIFIED" if verified else "NOT VERIFIED",
        "summary": "Verified PDF created and Telegram delivery confirmed." if verified else "PDF generation or Telegram delivery is not verified.",
        "file": file_info,
        "telegram_delivery": delivery,
        "evidence": [
            {"type": "file_exists", "path": file_info["path"], "size": file_info["size"]},
            {"type": "file_format", "format_ok": file_info["format_ok"], "extension": file_info["extension"]},
            {"type": "approved_dir", "approved_dir": file_info["approved_dir"]},
            {"type": "telegram_delivery", "ok": delivery["ok"], "returncode": delivery.get("returncode")},
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verified file generation and Telegram delivery for Hermes.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_test = sub.add_parser("generate-test-pdf")
    p_test.add_argument("--title", default="Hermes Test PDF")
    p_test.add_argument("--format", choices=["friendly", "json"], default="friendly")

    p_verify = sub.add_parser("verify-file")
    p_verify.add_argument("path")
    p_verify.add_argument("--format", choices=["friendly", "json"], default="friendly")

    p_message = sub.add_parser("from-message")
    p_message.add_argument("message")
    p_message.add_argument("--format", choices=["friendly", "json"], default="friendly")

    args = parser.parse_args()
    if args.cmd == "generate-test-pdf":
        file_info = create_pdf(args.title)
        data = {"verification_status": "VERIFIED" if file_info["verified"] else "NOT VERIFIED", "file": file_info}
    elif args.cmd == "verify-file":
        file_info = verify_file(Path(args.path))
        data = {"verification_status": "VERIFIED" if file_info["verified"] else "NOT VERIFIED", "file": file_info}
    else:
        data = from_message(args.message)

    if args.format == "json":
        print(json.dumps(data, ensure_ascii=False))
    else:
        print(mask(json.dumps(data, ensure_ascii=False)))
    return 0 if data.get("verification_status") == "VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
