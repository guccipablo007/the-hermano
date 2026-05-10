#!/usr/bin/env python3
import argparse, json, mimetypes, os, secrets, time, urllib.parse, urllib.request
from pathlib import Path
INDEX = Path("/root/.hermes/preview_links/index.json")
PUBLIC_HOST = os.environ.get("HERMES_PUBLIC_HOST", "162.222.206.158")
PREVIEW_PORT = int(os.environ.get("HERMES_PREVIEW_PORT", "9124"))
ALLOWED_ROOTS = [Path("/root/.hermes/newcoin_outputs"), Path("/root/.hermes/file_outputs"), Path("/root/.hermes/telegram_outputs"), Path("/root/.hermes/model_routing/test_outputs"), Path("/root/.hermes/rebuild_notes"), Path("/root/.hermes/scripts")]
ALLOWED_SEND_SUFFIXES = {".html", ".htm", ".pdf", ".docx", ".pptx", ".xlsx", ".md", ".txt", ".json", ".png", ".jpg", ".jpeg", ".webp", ".csv", ".py", ".zip"}
def is_allowed_path(path: Path):
    resolved = path.resolve()
    if not resolved.is_file() or resolved.suffix.lower() not in ALLOWED_SEND_SUFFIXES: return False
    for root in ALLOWED_ROOTS:
        rr = root.resolve()
        if resolved == rr or rr in resolved.parents: return True
    return False
def read_text_safe(path):
    try: return Path(path).read_text(errors="ignore")
    except Exception: return ""
def find_token_and_chat():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip() or os.environ.get("TELEGRAM_HOME_CHANNEL", "").strip()
    candidates = ["/root/.hermes/config.yaml", "/root/.hermes/.env", "/root/.hermes/telegram.env", "/root/.hermes/gateway.env", "/etc/systemd/system/hermes-gateway.service"]
    combined = "\n".join(read_text_safe(p) for p in candidates)
    if not token:
        import re
        m = re.search(r"(\d{6,}:[A-Za-z0-9_-]{20,})", combined)
        if m: token = m.group(1)
    if not chat_id:
        import re
        for key in ["TELEGRAM_CHAT_ID", "TELEGRAM_HOME_CHANNEL", "home_channel", "allowed_user", "allowed_users", "chat_id"]:
            m = re.search(rf"{key}[^0-9-]*(-?\d{{6,}})", combined, re.IGNORECASE)
            if m:
                chat_id = m.group(1); break
    if not chat_id: chat_id = "1969758159"
    if not token or not chat_id: raise SystemExit("TELEGRAM_TOKEN_OR_CHAT_ID_MISSING")
    return token, chat_id
def telegram_api(token, method, fields, file_path=None):
    url = f"https://api.telegram.org/bot{token}/{method}"
    if file_path:
        boundary = "----HermesBoundary" + secrets.token_hex(12); body = bytearray()
        def add_field(name, value):
            body.extend(f"--{boundary}\r\n".encode()); body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()); body.extend(str(value).encode()); body.extend(b"\r\n")
        for k, v in fields.items(): add_field(k, v)
        p = Path(file_path); mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        body.extend(f"--{boundary}\r\n".encode()); body.extend(f'Content-Disposition: form-data; name="document"; filename="{p.name}"\r\n'.encode()); body.extend(f"Content-Type: {mime}\r\n\r\n".encode()); body.extend(p.read_bytes()); body.extend(b"\r\n"); body.extend(f"--{boundary}--\r\n".encode())
        req = urllib.request.Request(url, data=bytes(body), method="POST"); req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    else:
        req = urllib.request.Request(url, data=urllib.parse.urlencode(fields).encode(), method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp: raw = resp.read().decode("utf-8")
    return json.loads(raw)
def register_preview(path: Path):
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    try: index = json.loads(INDEX.read_text())
    except Exception: index = {}
    token = secrets.token_urlsafe(16); index[token] = {"path": str(path.resolve()), "filename": path.name, "created_at": int(time.time())}
    INDEX.write_text(json.dumps(index, indent=2)); INDEX.chmod(0o600)
    return f"http://{PUBLIC_HOST}:{PREVIEW_PORT}/p/{token}"
def main():
    parser = argparse.ArgumentParser(description="Send Hermes outputs directly to Telegram.")
    parser.add_argument("--file", required=True); parser.add_argument("--caption", default=""); parser.add_argument("--preview-link", choices=["yes", "no", "auto"], default="auto"); parser.add_argument("--chat-id")
    args = parser.parse_args(); path = Path(args.file)
    if not is_allowed_path(path): raise SystemExit(f"FILE_NOT_ALLOWED_OR_NOT_FOUND: {path}")
    token, default_chat_id = find_token_and_chat(); chat_id = args.chat_id or default_chat_id
    caption = args.caption or f"Hermes output: {path.name}"
    telegram_api(token, "sendDocument", {"chat_id": chat_id, "caption": caption[:1000]}, file_path=path)
    preview_url = ""
    if args.preview_link == "yes" or (args.preview_link == "auto" and path.suffix.lower() in [".html", ".htm"]):
        preview_url = register_preview(path)
        telegram_api(token, "sendMessage", {"chat_id": chat_id, "text": f"Open Preview:\n{preview_url}", "disable_web_page_preview": "false"})
    print("TELEGRAM_DELIVERY=PASSED"); print("FILE=" + str(path)); print("DOCUMENT_SENT=yes"); print("PREVIEW_URL=" + preview_url)
if __name__ == "__main__": main()
