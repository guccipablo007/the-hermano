#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import secrets
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

INDEX = Path("/root/.hermes/preview_links/index.json")
PUBLIC_HOST = os.environ.get("HERMES_PUBLIC_HOST", "162.222.206.158")
PREVIEW_PORT = int(os.environ.get("HERMES_PREVIEW_PORT", "9124"))
ALLOWED_ROOTS = [
    Path("/root/.hermes/newcoin_outputs"),
    Path("/root/.hermes/file_outputs"),
    Path("/root/.hermes/telegram_outputs"),
    Path("/root/.hermes/model_routing/test_outputs"),
    Path("/root/.hermes/rebuild_notes"),
    Path("/root/.hermes/scripts"),
]
ALLOWED_SEND_SUFFIXES = {
    ".html", ".htm", ".pdf", ".docx", ".pptx", ".xlsx", ".md", ".txt",
    ".json", ".png", ".jpg", ".jpeg", ".webp", ".csv", ".py", ".zip",
}


def mask(text: Any) -> str:
    raw = str(text or "")
    raw = re.sub(r"bot\d+:[A-Za-z0-9_-]+", "<REDACTED>", raw)
    raw = re.sub(r"(chat_id|token)([\"':= ]+)([^,\s}\]]+)", r"\1\2<REDACTED>", raw, flags=re.I)
    raw = re.sub(r"(-?\d{8,})", "<chat_id_masked>", raw)
    return raw


def is_allowed_path(path: Path) -> bool:
    resolved = path.resolve()
    if not resolved.is_file() or resolved.suffix.lower() not in ALLOWED_SEND_SUFFIXES:
        return False
    return any(root.resolve() in resolved.parents or resolved == root.resolve() for root in ALLOWED_ROOTS)


def read_text_safe(path: str) -> str:
    try:
        return Path(path).read_text(errors="ignore")
    except Exception:
        return ""


def find_token_and_chat() -> tuple[str, str]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip() or os.environ.get("TELEGRAM_HOME_CHANNEL", "").strip()
    candidates = [
        "/root/.hermes/config.yaml",
        "/root/.hermes/.env",
        "/root/.hermes/telegram.env",
        "/root/.hermes/gateway.env",
        "/etc/systemd/system/hermes-gateway.service",
    ]
    combined = "\n".join(read_text_safe(p) for p in candidates)
    if not token:
        match = re.search(r"(\d{6,}:[A-Za-z0-9_-]{20,})", combined)
        if match:
            token = match.group(1)
    if not chat_id:
        for key in ["TELEGRAM_CHAT_ID", "TELEGRAM_HOME_CHANNEL", "home_channel", "allowed_user", "allowed_users", "chat_id"]:
            match = re.search(rf"{key}[^0-9-]*(-?\d{{6,}})", combined, re.IGNORECASE)
            if match:
                chat_id = match.group(1)
                break
    if not token or not chat_id:
        raise SystemExit("TELEGRAM_TOKEN_OR_CHAT_ID_MISSING")
    return token, chat_id


def telegram_api(token: str, method: str, fields: dict[str, Any], file_path: str | None = None) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{token}/{method}"
    if file_path:
        boundary = "----HermesBoundary" + secrets.token_hex(12)
        body = bytearray()

        def add_field(name: str, value: Any) -> None:
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
            body.extend(str(value).encode())
            body.extend(b"\r\n")

        for key, value in fields.items():
            add_field(key, value)
        path = Path(file_path)
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="document"; filename="{path.name}"\r\n'.encode())
        body.extend(f"Content-Type: {mime}\r\n\r\n".encode())
        body.extend(path.read_bytes())
        body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode())
        request = urllib.request.Request(url, data=bytes(body), method="POST")
        request.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    else:
        request = urllib.request.Request(url, data=urllib.parse.urlencode(fields).encode(), method="POST")
    with urllib.request.urlopen(request, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
        payload = json.loads(raw)
        payload["_http_status"] = getattr(resp, "status", None)
        return payload


def register_preview(path: Path) -> str:
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    try:
        index = json.loads(INDEX.read_text())
    except Exception:
        index = {}
    token = secrets.token_urlsafe(16)
    index[token] = {"path": str(path.resolve()), "filename": path.name, "created_at": int(time.time())}
    INDEX.write_text(json.dumps(index, indent=2))
    INDEX.chmod(0o600)
    return f"http://{PUBLIC_HOST}:{PREVIEW_PORT}/p/{token}"


def print_success(path: Path, preview_url: str, response: dict[str, Any]) -> None:
    print("TELEGRAM_DELIVERY=PASSED")
    print("TELEGRAM_API_OK=true")
    print("FILE=" + str(path))
    print("DOCUMENT_SENT=yes")
    print("PREVIEW_URL=" + preview_url)
    print("HTTP_STATUS=" + str(response.get("_http_status")))


def print_failure(path: Path, reason: str, response: dict[str, Any] | None = None) -> None:
    print("NOT VERIFIED")
    print("TELEGRAM_DELIVERY=FAILED")
    print("TELEGRAM_API_OK=false")
    print("FILE=" + str(path))
    print("REASON=" + mask(reason))
    if response:
        print("TELEGRAM_RESPONSE=" + mask(json.dumps({"ok": response.get("ok"), "description": response.get("description")}, ensure_ascii=False)))


def main() -> int:
    parser = argparse.ArgumentParser(description="Send Hermes outputs directly to Telegram.")
    parser.add_argument("--file", required=True)
    parser.add_argument("--caption", default="")
    parser.add_argument("--preview-link", choices=["yes", "no", "auto"], default="auto")
    parser.add_argument("--chat-id")
    args = parser.parse_args()

    path = Path(args.file)
    if not is_allowed_path(path):
        print_failure(path, f"FILE_NOT_ALLOWED_OR_NOT_FOUND:{path}")
        return 2

    try:
        token, default_chat_id = find_token_and_chat()
    except SystemExit as exc:
        print_failure(path, str(exc))
        return 2

    chat_id = args.chat_id or default_chat_id
    caption = args.caption or f"Hermes output: {path.name}"
    try:
        document_response = telegram_api(token, "sendDocument", {"chat_id": chat_id, "caption": caption[:1000]}, file_path=str(path))
    except Exception as exc:
        print_failure(path, f"SEND_DOCUMENT_EXCEPTION:{type(exc).__name__}")
        return 3
    if document_response.get("ok") is not True:
        print_failure(path, "SEND_DOCUMENT_NOT_OK", document_response)
        return 4

    preview_url = ""
    if args.preview_link == "yes" or (args.preview_link == "auto" and path.suffix.lower() in {".html", ".htm"}):
        preview_url = register_preview(path)
        try:
            preview_response = telegram_api(token, "sendMessage", {"chat_id": chat_id, "text": f"Open Preview:\n{preview_url}", "disable_web_page_preview": "false"})
        except Exception as exc:
            print_failure(path, f"SEND_PREVIEW_EXCEPTION:{type(exc).__name__}")
            return 5
        if preview_response.get("ok") is not True:
            print_failure(path, "SEND_PREVIEW_NOT_OK", preview_response)
            return 6

    print_success(path, preview_url, document_response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
